"""Génération d'images via l'API OpenAI (`POST /v1/images/generations`), exclusivement
côté serveur — même posture de sécurité que `app/ai/openai_provider.py` : la clé API
n'est jamais journalisée, jamais transmise au navigateur, jamais incluse dans un message
d'erreur (voir `_raise_for_error_response`, repris à l'identique).

Fournisseur SÉPARÉ du fournisseur texte (`OpenAIProvider`) : réutilise la même clé
(`settings.openai_api_key`), mais jamais `settings.openai_model` ni
`settings.ai_request_timeout_seconds`, qui restent réservés à la génération/correction
d'exercices (ticket #108 § 1 : « ne change pas les modèles ou paramètres utilisés pour les
examens »). Utilise ses propres réglages : `settings.openai_image_model` et
`settings.ai_image_request_timeout_seconds` (voir app/config.py).

Vérification de la documentation officielle avant implémentation (ticket #108 § 1,
2026-10) : endpoint REST `POST https://api.openai.com/v1/images/generations` ;
authentification identique (`Authorization: Bearer <clé>`) ; la réponse par défaut est déjà
`b64_json` (pas besoin de `response_format` explicite) ; une vérification d'organisation
peut être exigée par OpenAI avant l'accès aux modèles GPT Image — si l'appel échoue pour
cette raison, l'erreur OpenAI (`error.type`/`error.code`) est reprise telle quelle dans
`AIResponseError`, jamais masquée."""

import base64
import json

import httpx

from app.ai.provider import AINotConfiguredError, AIResponseError, AITimeoutError

IMAGES_URL = "https://api.openai.com/v1/images/generations"

# Voir app/ai/openai_provider.py::_MAX_ERROR_MESSAGE_LENGTH — même borne, même raison : un
# message d'erreur fournisseur ne doit jamais gonfler nos logs, et ne contient aucun secret.
_MAX_ERROR_MESSAGE_LENGTH = 200


class ImageProvider:
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

    @staticmethod
    def _raise_for_error_response(response: httpx.Response) -> None:
        error_payload: dict = {}
        try:
            body = response.json()
            if isinstance(body, dict) and isinstance(body.get("error"), dict):
                error_payload = body["error"]
        except (json.JSONDecodeError, ValueError):
            pass

        details = []
        error_type = error_payload.get("type")
        if error_type:
            details.append(f"type={error_type}")
        error_code = error_payload.get("code")
        if error_code:
            details.append(f"code={error_code}")
        error_message = error_payload.get("message")
        if error_message:
            truncated = str(error_message)[:_MAX_ERROR_MESSAGE_LENGTH]
            details.append(f"message={truncated!r}")

        detail_text = f" ({', '.join(details)})" if details else ""
        raise AIResponseError(
            f"Le service de génération d'images a répondu avec le statut "
            f"{response.status_code}{detail_text}."
        )

    def generate_image(
        self, prompt: str, size: str = "1024x1536", quality: str = "high"
    ) -> bytes:
        """Une seule image par appel (`n=1`). La politique de nouvelle tentative (au
        maximum une seconde, ticket #108 § 4) vit chez l'appelant
        (`app.v1.fse01_image.generate_and_save_poster_image`), jamais ici."""
        payload = {
            "model": self._model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": 1,
        }
        try:
            response = httpx.post(
                IMAGES_URL,
                headers=self._headers(),
                json=payload,
                timeout=self._timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise AITimeoutError(
                "Le service de génération d'images n'a pas répondu à temps."
            ) from exc
        except httpx.HTTPError as exc:
            raise AIResponseError(
                f"Erreur réseau vers le service de génération d'images : {exc}"
            ) from exc

        if response.status_code != 200:
            self._raise_for_error_response(response)

        try:
            data = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise AIResponseError("Réponse du service de génération d'images illisible.") from exc

        try:
            b64_data = data["data"][0]["b64_json"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIResponseError(
                "Réponse du service de génération d'images dans un format inattendu."
            ) from exc

        try:
            return base64.b64decode(b64_data)
        except (ValueError, TypeError) as exc:
            raise AIResponseError("Image reçue illisible (décodage base64 impossible).") from exc

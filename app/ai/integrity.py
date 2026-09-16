"""Signature légère (HMAC) des exercices générés par IA.

Le serveur ne conserve aucun état entre la génération et la correction d'un exercice IA
(pas de session, pas de table dédiée — architecture volontairement simple). Cette signature
garantit malgré tout que l'énoncé soumis à la correction est bien celui réellement produit
par ce serveur pour ce bloc et cette difficulté, et pas un texte arbitraire fourni par le
client : sans elle, la route de correction pourrait servir de proxy IA générique sans
rapport avec un cours borné. Réutilise `settings.secret_key` (déjà utilisé pour signer les
cookies de session) : aucun nouveau secret à gérer.
"""

import hashlib
import hmac

from app.config import settings


def sign_exercise(block_id: int, difficulty: str, exercise_type: str, statement: str) -> str:
    message = f"{block_id}|{difficulty}|{exercise_type}|{statement}".encode()
    return hmac.new(settings.secret_key.encode(), message, hashlib.sha256).hexdigest()


def verify_exercise_signature(
    block_id: int, difficulty: str, exercise_type: str, statement: str, signature: str
) -> bool:
    expected = sign_exercise(block_id, difficulty, exercise_type, statement)
    return hmac.compare_digest(expected, signature)

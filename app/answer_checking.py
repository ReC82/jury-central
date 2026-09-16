import unicodedata
from fractions import Fraction


def parse_answer(raw: str) -> Fraction | None:
    """Parse une réponse étudiante en Fraction exacte.

    Accepte les entiers, les décimaux (virgule ou point) et les fractions
    "a/b" — délégué au parseur natif de `Fraction`, qui gère déjà ces trois
    formats. Aucun `eval()`.
    """
    trimmed = (raw or "").strip().replace(" ", "")
    if not trimmed:
        return None
    normalized = trimmed.replace(",", ".")
    try:
        return Fraction(normalized)
    except (ValueError, ZeroDivisionError):
        return None


def answers_match(expected: Fraction, submitted: str) -> bool:
    """Compare une réponse soumise à la réponse attendue, égalité exacte."""
    value = parse_answer(submitted)
    if value is None:
        return False
    return value == expected


def normalize_text(raw: str) -> str:
    """Normalise une réponse textuelle courte pour une comparaison insensible à la casse,
    aux espaces superflus et aux accents (ex. "Ram" / "ram " / "râm" comparés égaux).

    Sert uniquement à la comparaison (voir `text_answer_matches`) — ne modifie jamais le
    contenu pédagogique affiché.
    """
    collapsed = " ".join((raw or "").strip().split())
    decomposed = unicodedata.normalize("NFKD", collapsed)
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_accents.lower()


def text_answer_matches(accepted: list[str], submitted: str) -> bool:
    """Compare une réponse textuelle courte à une liste de réponses acceptées, après
    normalisation (voir `normalize_text`). Aucun `eval()`. Une réponse soumise vide n'est
    jamais considérée correcte, même si une réponse acceptée est elle-même vide."""
    normalized_submitted = normalize_text(submitted)
    if not normalized_submitted:
        return False
    return any(normalize_text(candidate) == normalized_submitted for candidate in accepted)

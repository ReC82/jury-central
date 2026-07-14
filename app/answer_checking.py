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

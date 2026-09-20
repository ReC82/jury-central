import re
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


# --- Ticket #90 § 8 : réponse numérique noyée dans une phrase explicative --------------------

_NUMBER_TOKEN_RE = re.compile(r"-?\d+(?:[.,]\d+)?")


def extract_last_number(raw: str) -> Fraction | None:
    """Extrait le DERNIER nombre présent dans un texte libre (ticket #90 § 8) — cas réel :
    « 256 - 248 = 8, donc 8 est l'incrément » doit être reconnu comme la valeur 8, jamais
    rejeté parce que la réponse entière n'est pas un nombre nu.

    Règle STRUCTURÉE et bornée, pas un fuzzy matching général (§ 8 du ticket, « ne
    généralise pas ») : retient délibérément le DERNIER nombre, jamais « n'importe quel
    nombre présent » — une réponse qui mentionne une valeur intermédiaire ou explicitement
    rejetée avant de conclure sur la bonne valeur (« ce n'est pas 16, c'est 8 ») doit
    encore pouvoir échouer si sa VRAIE conclusion (le dernier nombre) est fausse ; retenir
    n'importe quel nombre présent accepterait à tort une réponse qui cite la bonne valeur
    en passant avant de conclure autre chose."""
    matches = _NUMBER_TOKEN_RE.findall(raw or "")
    if not matches:
        return None
    try:
        return Fraction(matches[-1].replace(",", "."))
    except (ValueError, ZeroDivisionError):
        return None


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


# --- Tickets #85/#90 § 9 : distinguer un short_answer factuel d'un short_answer sémantique ----
#
# Module PARTAGÉ (jamais dupliqué) entre `app.v1.short_answer_limits` (limite de longueur,
# #85) et `app.ai.schemas`/`app.ai.local_correction` (#90 : une question qui demande une
# démarche/justification/comparaison ne doit JAMAIS être notée par égalité textuelle
# stricte, même si son `accepted_answers` est renseigné). Détection volontairement bornée
# (liste de déclencheurs lexicaux + un motif « N + mot »), jamais un raisonnement sémantique
# complet — voir la docstring de `is_semantic_short_answer_prompt`.

_SEMANTIC_SHORT_ANSWER_TRIGGERS_NORMALIZED = (
    "explique", "expliquer", "expliquez", "explication",
    "justifie", "justifier", "justifiez", "justification",
    "compare", "comparer", "comparez", "comparaison",
    "decris", "decrire", "decrivez", "decrivant",
    "demarche",
    "pourquoi",
)

# « cite/donne/liste deux/trois/N X » (ex. « Cite deux contrôles à effectuer ») : un nombre
# suivi de n'importe quel mot, pas une liste de noms fermée — un « N + mot » dénote presque
# toujours une énumération à développer, jamais un simple rappel factuel isolé.
_SEMANTIC_SHORT_ANSWER_MULTI_PART_RE = re.compile(
    r"\b(deux|trois|quatre|cinq|six|sept|huit|neuf|dix|\d+)\s+\w+"
)


def is_semantic_short_answer_prompt(prompt: str) -> bool:
    """Vrai si l'énoncé d'un `short_answer`/`vocabulary` demande une réponse développée
    (démarche, justification, comparaison, explication, plusieurs éléments à développer)
    — auquel cas la question ne doit JAMAIS être corrigée par égalité textuelle stricte,
    même si un `accepted_answers` existe (§ 90.2/90.9 du ticket : « une short_answer/
    long_answer demandant justification/démarche/comparaison/diagnostic/explication ne
    doit jamais tomber sur une égalité textuelle stricte comme correction finale »).

    Portée volontairement bornée (pas de NLP) : une liste de déclencheurs lexicaux fixe +
    un motif structurel « nombre + mot » — jamais une compréhension sémantique de
    l'énoncé. Le risque asymétrique justifie une détection généreuse : un faux positif
    envoie une question réellement factuelle à l'IA (coût négligeable, jamais une mauvaise
    note) ; un faux négatif laisserait une vraie question sémantique se faire noter par
    une égalité textuelle stricte (le bug réel que ce ticket corrige)."""
    normalized = normalize_text(prompt)
    if any(trigger in normalized for trigger in _SEMANTIC_SHORT_ANSWER_TRIGGERS_NORMALIZED):
        return True
    return bool(_SEMANTIC_SHORT_ANSWER_MULTI_PART_RE.search(normalized))

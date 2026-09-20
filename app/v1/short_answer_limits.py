"""Limite dynamique de longueur pour `short_answer`/`vocabulary` (ticket #85).

Cas réel : une question de comparaison HDD / SSD SATA / SSD NVMe coupait la réponse de
l'utilisateur à 200/200 caractères — l'utilisateur avait une bonne réponse mais voulait
la compléter. Cause racine : `ShortAnswerContent.max_length` (`app/v1/question_types.py`)
ne recevait JAMAIS de valeur explicite lors de la construction du contenu (ni depuis la
génération IA — `app/v1/ai_bridge.py` — ni depuis l'import éditorial legacy —
`app/v1/bank.py`), donc retombait systématiquement sur son défaut Pydantic (200), quelle
que soit la nature réelle de la question demandée.

Règle produit (§ 85.A) :
- réponse factuelle très courte (« Que signifie SMART ? », « Quel est l'incrément d'un
  /26 ? ») : 100-300 caractères ;
- réponse expliquée/justifiée/comparée (déclencheurs : explique, justifie, compare,
  décris, quelle démarche, pourquoi, « donne X éléments et explique », plusieurs
  sous-parties) : 800-1500 caractères minimum ;
- réponse nécessitant plusieurs paragraphes : ce n'est plus un `short_answer`, voir
  `long_answer` (décision de RETYPAGE, hors de portée de ce module — § 85.C, cas par cas,
  jamais une bascule automatique aveugle).

Détection volontairement bornée (pas de NLP complexe, § 85.B) : déléguée à
`app.answer_checking.is_semantic_short_answer_prompt`, partagée avec le ticket #90
(garde de correction — une question sémantique ne doit jamais être notée par égalité
textuelle stricte) pour ne jamais maintenir deux listes de déclencheurs divergentes.
"""

from app.answer_checking import is_semantic_short_answer_prompt

FACTUAL_DEFAULT_MAX_LENGTH = 300
DEVELOPED_DEFAULT_MAX_LENGTH = 1500

# Seuil au-delà duquel un max_length est considéré « factuel » (donc potentiellement
# incohérent avec un énoncé qui demande explicitement une réponse développée, § 85.B).
_FACTUAL_CEILING = 300


def compute_short_answer_max_length(prompt: str) -> int:
    """Longueur maximale à attribuer à un `short_answer`/`vocabulary`, déterminée à
    partir de la formulation de l'énoncé — jamais une valeur fixe unique pour toutes les
    questions (§ 85.A). Ne tronque jamais une réponse correcte à cause d'une limite
    artificielle (§ 85.B) : en cas de doute (déclencheur détecté), la limite large est
    retenue."""
    if is_semantic_short_answer_prompt(prompt):
        return DEVELOPED_DEFAULT_MAX_LENGTH
    return FACTUAL_DEFAULT_MAX_LENGTH


def is_max_length_incoherent(prompt: str, max_length: int) -> bool:
    """§ 85.B — filet de sécurité indépendant de `compute_short_answer_max_length` :
    détecte l'incohérence produit (énoncé qui demande explicitement une réponse
    développée/justifiée/comparée, mais limite restée factuelle ≤ 300) quelle que soit la
    façon dont `max_length` a été fixé — génération IA, import éditorial, ou modification
    manuelle ultérieure."""
    return is_semantic_short_answer_prompt(prompt) and max_length <= _FACTUAL_CEILING

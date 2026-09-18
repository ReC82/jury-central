"""Détection de quasi-doublons entre questions (ticket #64, priorités 1/2).

Constat de départ (validation staging du ticket #62) : un examen blanc peut présenter à
l'utilisateur une question textuellement quasi identique à une déjà vue en entraînement,
même quand il ne s'agit techniquement PAS de la même `Question` (banque alimentée par
génération IA au fil des sessions, § BANQUE MVP du ticket #55) — l'exclusion « déjà vue »
par `question_id`/`UserQuestionHistory` (ticket #38 § J) ne suffit donc pas seule.

Ce module fournit une SIGNATURE STRUCTURELLE, calculée localement (aucun appel IA, aucun
réseau — comparaison déterministe, testable sans provider) : type de question + libellés
structurels (options/éléments/catégories/items, triés — un simple réordonnancement ne doit
JAMAIS suffire à rendre une question « nouvelle », § 2 du ticket) + ensemble de mots
significatifs de l'énoncé normalisé. Deux questions sont considérées quasi-doublons si leur
structure triée est strictement identique, OU si leurs énoncés partagent une proportion
élevée de mots significatifs (Jaccard) — repère volontairement approximatif : reste un
filet de sécurité mécanique, pas un jugement pédagogique fin.

Utilisé par `app.v1.bank` (exclusion à la sélection ET au moment de persister une question
générée) — jamais pour la correction (voir `app.v1.hybrid_correction`, sans lien)."""

from app.answer_checking import normalize_text

# Sous ce seuil de recouvrement lexical de l'énoncé (mots significatifs communs / union),
# deux questions du même type ne sont plus considérées comme un quasi-doublon — calibré
# empiriquement (voir tests) : assez haut pour ne jamais confondre deux notions
# différentes, assez bas pour attraper une simple reformulation superficielle.
PROMPT_SIMILARITY_THRESHOLD = 0.72

# Deux questions à la structure IDENTIQUE (mêmes options/éléments/catégories, triés) mais
# dont les énoncés ne partagent presque AUCUN mot significatif ne sont pas un quasi-doublon
# malgré la structure identique — ex. deux QCM binaires qui réutilisent coïncidemment le
# même couple d'options générique (« Vrai »/« Faux », ou deux mêmes libellés de distracteur)
# pour des notions totalement différentes. Seuil volontairement bas : sert uniquement à
# écarter les collisions structurelles fortuites, pas à exiger une vraie proximité.
STRUCTURAL_MATCH_MIN_PROMPT_OVERLAP = 0.15

# Mots trop fréquents/peu discriminants en français pour compter dans la comparaison
# d'énoncés (déterminants, prépositions courantes, pronoms) — liste volontairement courte,
# suffisante pour ce cas d'usage (jamais un vrai traitement linguistique).
_STOPWORDS = frozenset(
    {
        "le", "la", "les", "un", "une", "des", "de", "du", "au", "aux", "et", "ou", "est",
        "que", "qui", "quel", "quelle", "quels", "quelles", "pour", "dans", "sur", "ce",
        "cette", "ces", "avec", "son", "sa", "ses", "il", "elle", "vous", "tu", "on",
        "en", "par", "plus", "entre", "sont", "comment", "quoi", "faut",
    }
)

# Types dont le libellé structurel se lit sur ces clés de `content_json` (forme du
# registre #40, voir `app.v1.ai_bridge` pour le détail par type) — un type absent de cette
# table n'a pas de structure comparable (ex. long_answer/diagnostic/procedure : seul
# l'énoncé compte, comparé via le recouvrement lexical).
_STRUCTURAL_FIELDS: dict[str, tuple[str, ...]] = {
    "multiple_choice": ("options",),
    "single_choice": ("options",),
    "true_false": ("options",),
    "classification": ("categories", "elements"),
    "ordering": ("items",),
    "matching": ("pairs_left", "pairs_right"),
    "short_answer": ("accepted_answers",),
    "vocabulary": ("accepted_answers",),
    "fill_blank": ("accepted_answers",),
}


def _label_of(entry: object) -> str:
    if isinstance(entry, dict):
        return str(entry.get("label", entry.get("option_id", "")))
    return str(entry)


def _structural_labels(question_type: str, content: dict) -> tuple[str, ...]:
    """Libellés structurels normalisés et TRIÉS (indépendants de l'ordre — voir docstring
    du module) pour les champs pertinents de ce type. Tuple vide si le type n'a pas de
    structure comparable (types purement rédigés)."""
    fields = _STRUCTURAL_FIELDS.get(question_type, ())
    labels: list[str] = []
    for field_name in fields:
        for entry in content.get(field_name) or []:
            label = normalize_text(_label_of(entry))
            if label:
                labels.append(label)
    return tuple(sorted(labels))


def _significant_words(text: str) -> frozenset[str]:
    normalized = normalize_text(text or "")
    return frozenset(word for word in normalized.split() if len(word) > 2 and word not in _STOPWORDS)


class QuestionSignature:
    """Signature comparable d'une question, pour `is_near_duplicate`. Immuable, ne porte
    aucune donnée privée (solution) — uniquement énoncé/structure déjà publics."""

    __slots__ = ("prompt_words", "question_type", "structural_labels")

    def __init__(self, question_type: str, content: dict) -> None:
        self.question_type = question_type
        self.structural_labels = _structural_labels(question_type, content)
        self.prompt_words = _significant_words(content.get("prompt", "") if isinstance(content, dict) else "")


def question_signature(question_type: str, content: dict) -> QuestionSignature:
    return QuestionSignature(question_type, content if isinstance(content, dict) else {})


def is_near_duplicate(a: QuestionSignature, b: QuestionSignature) -> bool:
    """Vrai si `a`/`b` sont un quasi-doublon : même type, ET
    - recouvrement lexical de l'énoncé au-dessus de `PROMPT_SIMILARITY_THRESHOLD` (attrape
      une reformulation superficielle, structure ou non identique), OU
    - structure triée strictement identique (un réordonnancement pur ne suffit jamais à
      échapper à cette règle) MAIS seulement si les énoncés partagent au moins un peu de
      vocabulaire (`STRUCTURAL_MATCH_MIN_PROMPT_OVERLAP`) — écarte la collision fortuite de
      deux questions différentes qui réutilisent par hasard le même jeu d'options/éléments
      générique (voir docstring de ce seuil)."""
    if a.question_type != b.question_type:
        return False
    jaccard = 0.0
    if a.prompt_words and b.prompt_words:
        union = a.prompt_words | b.prompt_words
        if union:
            jaccard = len(a.prompt_words & b.prompt_words) / len(union)
    if jaccard >= PROMPT_SIMILARITY_THRESHOLD:
        return True
    if a.structural_labels and a.structural_labels == b.structural_labels:
        return jaccard >= STRUCTURAL_MATCH_MIN_PROMPT_OVERLAP
    return False


def find_near_duplicate(
    signature: QuestionSignature, candidates: list[QuestionSignature]
) -> QuestionSignature | None:
    for candidate in candidates:
        if is_near_duplicate(signature, candidate):
            return candidate
    return None

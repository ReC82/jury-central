"""Validation QUALITÉ des questions générées (ticket #69), complémentaire au validateur
métier IPv4/subnetting (`app.v1.domain_validation`, ticket #68).

Différence avec `app.v1.domain_validation`
--------------------------------------------
`app.v1.domain_validation` vérifie la VÉRITÉ TECHNIQUE d'une question (une adresse
broadcast n'est jamais un hôte valide, un masque correspond à son CIDR...). Ce module
vérifie sa CLARTÉ/QUALITÉ PÉDAGOGIQUE — une question peut être techniquement irréprochable
tout en étant trop facile, ambiguë ou en donnant la réponse dans l'énoncé. Constats réels
(tests utilisateurs, staging) :

- un `ordering` affichait ses éléments déjà dans le bon ordre (« il suffit de choisir
  1, 2, 3, 4, 5, 6 ») — le correctif PRINCIPAL est préventif
  (`app.v1.ai_bridge.shuffle_ordering_items`, appliqué à la création du contenu) ; ce
  module ajoute un filet de sécurité qui détecte et rejette le cas résiduel ;
- un exercice CIDR donnait déjà les bornes de la réponse dans l'énoncé
  (« ... en partant du plus petit (/30) jusqu'au plus grand (/24) ») ;
- une classification reposait sur une formulation molle (« souvent choisi »,
  « généralement utilisé ») plutôt qu'un critère technique observable ;
- une question `diagnostic` ne fournissait aucun contexte concret exploitable
  (« Après avoir vérifié l'adresse IP, que vérifier ensuite ? » — quel test, quel
  résultat ?).

Portée volontairement bornée, sans NLP (§ 9 du ticket) : ce module ne tente PAS de juger
la plausibilité sémantique de distracteurs (« QCM dont plusieurs distracteurs sont
manifestement hors domaine ») — un tel jugement nécessiterait une compréhension du
contenu hors de portée d'un contrôle syntaxique fiable. Cette exigence est couverte par le
prompt de génération (`app.ai.prompts`) et par des tests ciblés sur des cas concrets,
jamais par un raisonnement IA supplémentaire côté serveur.

Même architecture de registre extensible que `app.v1.domain_validation` :

```python
QUALITY_VALIDATORS = [validate_question_quality_rules]

def validate_question_quality(module, uaa, question_type, content_json) -> list[str]:
    ...
```
"""

import re
from typing import Any, Protocol

from app.answer_checking import normalize_text

# --- Détection § 8 : formulations molles qui décident seules d'une classification ----------

_WEAK_PHRASES = (
    "souvent choisi", "souvent utilise", "generalement utilise", "generalement choisi",
    "habituellement utilise", "le plus souvent",
)

# --- Détection § 6/7 : question diagnostic sans contexte concret exploitable ----------------

_CONCRETE_DIGIT_RE = re.compile(r"\d")
_CONCRETE_COMMAND_RE = re.compile(r"`[^`]+`")
_OUTCOME_KEYWORDS = (
    "echoue", "reussi", "repond", "affiche", "resultat", "observe", "indique", "mesure",
    "accessible", "inaccessible", "actif", "inactif",
)

# --- Détection § 3/10 : CIDR trop guidé (bornes de la réponse données dans l'énoncé) --------

_BARE_CIDR_TOKEN_RE = re.compile(r"/(2[4-9]|30)\b")


def _prompt_of(content: dict[str, Any]) -> str:
    return str(content.get("prompt", "")) if isinstance(content, dict) else ""


def _check_ordering_not_shuffled(question_type: str, content: dict[str, Any]) -> list[str]:
    """Filet de sécurité (§ 2/9) : le correctif principal est préventif
    (`app.v1.ai_bridge.shuffle_ordering_items`) — cette règle ne devrait donc normalement
    jamais se déclencher, mais protège contre un contournement (ex. contenu injecté
    autrement que via le pont IA)."""
    if question_type != "ordering":
        return []
    items = content.get("items") or []
    correct_order = content.get("correct_order") or []
    if len(items) < 2:
        return []
    displayed_ids = [item.get("id") if isinstance(item, dict) else item for item in items]
    if displayed_ids == list(correct_order):
        message = (
            "Ordering affiché exactement dans l'ordre attendu — l'exercice ne demande "
            "plus aucun raisonnement (il suffit de choisir 1, 2, 3...)."
        )
        return [message]
    return []


def _check_weak_classification_phrasing(question_type: str, content: dict[str, Any]) -> list[str]:
    """§ 8/9 : une formulation molle (« souvent choisi », « généralement utilisé ») ne
    peut pas être le SEUL critère déterminant une classification — une propriété
    technique observable est attendue à la place."""
    if question_type not in ("classification", "multiple_choice"):
        return []
    texts = [_prompt_of(content)]
    for category in content.get("categories") or []:
        texts.append(str(category))
    for option in content.get("options") or []:
        texts.append(str(option.get("label", "")) if isinstance(option, dict) else str(option))
    normalized = normalize_text(" ".join(texts))
    matched = [phrase for phrase in _WEAK_PHRASES if phrase in normalized]
    if matched:
        message = (
            "Formulation trop faible pour déterminer une classification "
            f"({', '.join(matched)}) — préférer une propriété technique observable."
        )
        return [message]
    return []


def _check_diagnostic_self_sufficiency(question_type: str, content: dict[str, Any]) -> list[str]:
    """§ 6/7 : une question `diagnostic` doit contenir tout le contexte nécessaire
    (symptôme observé, résultat de test, état) — jamais un simple « et ensuite ? » sans
    aucune donnée concrète exploitable. Détection bornée : présence d'au moins un marqueur
    concret (un chiffre — adresse/valeur mesurée, un token entre backticks — commande/
    sortie, ou un mot-clé de résultat explicitement observé)."""
    if question_type != "diagnostic":
        return []
    prompt = _prompt_of(content)
    if _CONCRETE_DIGIT_RE.search(prompt):
        return []
    if _CONCRETE_COMMAND_RE.search(prompt):
        return []
    normalized = normalize_text(prompt)
    if any(keyword in normalized for keyword in _OUTCOME_KEYWORDS):
        return []
    message = (
        "Question diagnostic sans contexte concret exploitable (aucune valeur mesurée, "
        "aucune commande/sortie, aucun résultat de test observé décrit) — reformuler avec "
        "une vraie mise en situation autosuffisante."
    )
    return [message]


def _check_cidr_overguided(question_type: str, content: dict[str, Any]) -> list[str]:
    """§ 3/10 : un exercice qui demande de classer/ordonner des préfixes CIDR ne doit pas
    révéler une partie de la réponse (les bornes) directement dans l'énoncé — ex. « ... en
    partant du plus petit (/30) jusqu'au plus grand (/24) »."""
    if question_type not in ("ordering", "classification"):
        return []
    if question_type == "ordering":
        tokens = [item.get("label", "") if isinstance(item, dict) else str(item) for item in content.get("items") or []]
    else:
        tokens = [str(e) for e in content.get("elements") or []]

    prefix_tokens = {m.group(0) for token in tokens for m in [_BARE_CIDR_TOKEN_RE.search(str(token).strip())] if m}
    if not prefix_tokens:
        return []

    prompt = _prompt_of(content)
    leaked = sorted(p for p in prefix_tokens if p in prompt)
    if leaked:
        message = (
            "L'énoncé révèle directement une partie de la réponse (bornes du classement/"
            f"ordre données en toutes lettres : {', '.join(leaked)}) — reformuler sans "
            "donner les préfixes extrêmes dans le texte (ex. associer préfixe ↔ nombre "
            "d'hôtes, ou choisir le bon préfixe pour un besoin donné)."
        )
        return [message]
    return []


_SUPPORTED_TYPES = frozenset({"multiple_choice", "classification", "ordering", "diagnostic"})


def validate_question_quality_rules(
    module: Any, uaa: Any, question_type: str, content_json: dict[str, Any]
) -> list[str]:
    """Point d'entrée du domaine QUALITÉ (§ 4-9 du ticket #69). Retourne une liste
    d'erreurs explicites (vide = question acceptée). Ignore silencieusement tout type non
    concerné, comme `app.v1.domain_validation.validate_ipv4_subnet_question`."""
    if question_type not in _SUPPORTED_TYPES or not isinstance(content_json, dict):
        return []

    errors: list[str] = []
    errors.extend(_check_ordering_not_shuffled(question_type, content_json))
    errors.extend(_check_weak_classification_phrasing(question_type, content_json))
    errors.extend(_check_diagnostic_self_sufficiency(question_type, content_json))
    errors.extend(_check_cidr_overguided(question_type, content_json))
    return errors


class QualityValidator(Protocol):
    def __call__(
        self, module: Any, uaa: Any, question_type: str, content_json: dict[str, Any]
    ) -> list[str]: ...


# Registre extensible, même principe que `app.v1.domain_validation.DOMAIN_VALIDATORS`.
QUALITY_VALIDATORS: list[QualityValidator] = [validate_question_quality_rules]


def validate_question_quality(
    module: Any, uaa: Any, question_type: str, content_json: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    for validator in QUALITY_VALIDATORS:
        errors.extend(validator(module, uaa, question_type, content_json))
    return errors

"""Registre extensible des types de questions V1 (ticket #40).

Fournit LE CONTRAT que consommeront la banque (#41), l'autosave (#42), la génération
(#43), la correction (#44) et l'admin (#46) — ce module ne construit ni sélection, ni
API HTTP, ni génération, ni correction batch, uniquement l'abstraction centrale.

Vocabulaire délibérément aligné sur l'existant (voir audit,
`docs/claude-reports/2026-09-17_ticket-40_question-engine-v1.md`) pour ne jamais avoir
trois vocabulaires incompatibles dans le projet :

- Les identifiants de type déjà partagés par `app.ai.schemas.QUESTION_TYPES` (ticket
  #23) et `app.editorial_exercise.EDITORIAL_EXERCISE_TYPES` (ticket #17/#21/#29) —
  `short_answer`, `long_answer`, `fill_blank`, `matching`, `classification`, `ordering`,
  `numeric`, `diagnostic`, `procedure`, `vocabulary` — gardent EXACTEMENT le même nom
  ici.
- **Déviation assumée et documentée** : ce registre ne définit pas `single_choice`
  séparément (consigne explicite du ticket #40) — `multiple_choice` couvre le cas
  `min_selections=max_selections=1`. Les vocabulaires existants (#17/#21/#23/#29)
  gardent `single_choice` comme type séparé pour LEUR périmètre déjà déployé (MC01/MC02/
  MC03) : aucune migration de ce contenu n'est faite par ce ticket, les deux
  coexistent le temps que #41+ bascule effectivement la banque sur ce nouveau registre.
- Correction locale déterministe : réutilise `app.answer_checking`
  (`text_answer_matches`, `parse_answer`/`answers_match`) plutôt que de réimplémenter la
  comparaison texte/numérique — jamais de second mécanisme de normalisation de texte, et
  jamais de `eval()`.
- `AssetKind` réutilisé tel quel depuis `app.v1.models` (ticket #38) — pas de second
  vocabulaire d'assets.

Sécurité structurelle (voir § « Payload public/privé ») : `public_payload()` est le SEUL
point d'entrée qui transforme un `content_json` interne en JSON envoyé au navigateur —
implémenté en listant explicitement les champs publics (jamais en retirant les champs
privés d'une copie), pour qu'un nouveau champ de solution ajouté à un type ne puisse
jamais fuiter par oubli."""

from __future__ import annotations

import enum
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from app.v1.models import AssetKind


class QuestionEngineError(ValueError):
    """Erreur de contrat (type inconnu, version de schéma inconnue) — jamais confondue
    avec une erreur de VALIDATION de contenu (voir `ContentValidationError`)."""


class ContentValidationError(ValueError):
    """`content_json` ou `answer_json` structurellement invalide pour son type. Le
    message ne doit jamais contenir de solution (voir chaque type dans
    `app/v1/question_types.py` : les erreurs Pydantic portent sur la FORME, jamais sur la
    valeur attendue)."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors) or "contenu invalide")
        self.errors = errors


class Capability(str, enum.Enum):
    """Ce qu'un type de question exige du frontend — le futur composant d'affichage
    choisit son widget à partir de cet ensemble, jamais en testant la matière (§
    « Composition » du ticket)."""

    TEXT_INPUT = "text_input"
    MULTI_SELECT = "multi_select"
    ORDERABLE = "orderable"
    DRAG_DROP = "drag_drop"
    IMAGE = "image"
    SVG = "svg"
    GRAPH = "graph"
    DOCUMENT = "document"
    TABLE = "table"
    CODE = "code"
    FORMULA = "formula"
    HOTSPOT = "hotspot"
    SEMANTIC_GRADING = "semantic_grading"
    LOCAL_GRADING = "local_grading"


class CorrectionMode(str, enum.Enum):
    """Modalité de correction déclarée par type — consommée par le ticket #44.

    Codifie explicitement ce qui n'existait jusqu'ici que comme des frozensets implicites
    (`app.ai.schemas.DETERMINISTIC_QUESTION_TYPES` et consorts) : même concept, rendu
    interrogeable par type plutôt que par appartenance à un ensemble figé."""

    LOCAL = "local"
    SEMANTIC_AI = "semantic_ai"
    HYBRID = "hybrid"


class SourceDocumentRequirement(str, enum.Enum):
    NONE = "none"
    OPTIONAL = "optional"
    REQUIRED = "required"
    MULTIPLE = "multiple"


@dataclass(frozen=True)
class AssetContract:
    """Ce qu'un type de question peut/doit référencer comme `Asset` (ticket #38, §F).

    `allowed_kinds` vide = aucun asset supporté. `min_assets > 0` implique
    `requires_asset` (propriété dérivée, jamais un second booléen qui pourrait diverger)."""

    allowed_kinds: frozenset[AssetKind] = frozenset()
    min_assets: int = 0
    max_assets: int = 0

    def __post_init__(self) -> None:
        if self.min_assets < 0 or self.max_assets < 0:
            raise QuestionEngineError("min_assets/max_assets doivent être >= 0.")
        if self.max_assets and self.min_assets > self.max_assets:
            raise QuestionEngineError("min_assets ne peut pas dépasser max_assets.")
        if self.max_assets and not self.allowed_kinds:
            raise QuestionEngineError("max_assets > 0 nécessite allowed_kinds non vide.")

    @property
    def requires_asset(self) -> bool:
        return self.min_assets > 0


NO_ASSET = AssetContract()


@dataclass(frozen=True)
class QuestionTypeSpec:
    """Une entrée du registre — LE CONTRAT pour un type de question.

    `content_model`/`answer_model` : classes Pydantic (déjà une dépendance du projet via
    FastAPI, utilisées directement ailleurs — voir `app/admin.py`, `app/practice.py`) —
    validation, messages d'erreur et (dé)sérialisation JSON obtenus sans réimplémenter un
    système de schéma pour chacun des 26 types.

    `check_answer` : `None` pour un type toujours `SEMANTIC_AI` (aucune correction locale
    possible). Pour `LOCAL`/`HYBRID`, retourne un booléen — ou lève
    `RequiresSemanticCorrection` si CE contenu précis (ex. short_answer sans
    accepted_answers) doit basculer vers l'IA malgré un mode global `HYBRID`."""

    type_id: str
    schema_versions: frozenset[int]
    correction_mode: CorrectionMode
    capabilities: frozenset[Capability]
    asset_contract: AssetContract
    source_document_requirement: SourceDocumentRequirement
    content_model: type[BaseModel]
    answer_model: type[BaseModel]
    to_public: Callable[[BaseModel], dict[str, Any]]
    check_answer: Callable[[BaseModel, BaseModel], bool] | None
    description: str = ""

    def requires_semantic_correction(self, content: BaseModel) -> bool:
        """Vrai si CE contenu précis doit être corrigé par l'IA — toujours vrai pour
        `SEMANTIC_AI`, jamais pour `LOCAL`, dépend du contenu pour `HYBRID` (ex.
        short_answer sans `accepted_answers`). Jamais l'inverse d'un test sur la
        présence de la solution : chaque type HYBRID expose son propre indicateur via
        `content.requires_semantic` (voir `app/v1/question_types.py`)."""
        if self.correction_mode == CorrectionMode.SEMANTIC_AI:
            return True
        if self.correction_mode == CorrectionMode.LOCAL:
            return False
        return bool(getattr(content, "requires_semantic", lambda: False)())


class RequiresSemanticCorrection(Exception):
    """Levée par un `check_answer` HYBRID quand ce contenu précis n'est pas corrigeable
    localement — signal, pas une erreur applicative."""


class QuestionTypeRegistry:
    """Registre central — pas de if/elif dispersé : chaque route/service consulte cette
    seule table pour connaître le contrat d'un type."""

    def __init__(self) -> None:
        self._specs: dict[str, QuestionTypeSpec] = {}

    def register(self, spec: QuestionTypeSpec) -> None:
        if spec.type_id in self._specs:
            raise QuestionEngineError(f"type déjà enregistré : {spec.type_id!r}.")
        if not spec.schema_versions:
            raise QuestionEngineError(f"{spec.type_id} : au moins une schema_version requise.")
        self._specs[spec.type_id] = spec

    def get(self, type_id: str) -> QuestionTypeSpec:
        try:
            return self._specs[type_id]
        except KeyError:
            raise QuestionEngineError(f"type de question inconnu : {type_id!r}.") from None

    def list_types(self) -> list[QuestionTypeSpec]:
        return sorted(self._specs.values(), key=lambda spec: spec.type_id)

    def __contains__(self, type_id: str) -> bool:
        return type_id in self._specs


QUESTION_TYPE_REGISTRY = QuestionTypeRegistry()


def _require_schema_version(spec: QuestionTypeSpec, schema_version: int) -> None:
    if schema_version not in spec.schema_versions:
        raise QuestionEngineError(
            f"{spec.type_id} : schema_version {schema_version!r} non supportée "
            f"(supportées : {sorted(spec.schema_versions)})."
        )


def _pydantic_errors(exc: ValidationError) -> list[str]:
    """Messages d'erreur Pydantic réduits à l'emplacement + le message — jamais la
    valeur soumise en entier (pourrait contenir une tentative de solution à ne pas
    journaliser telle quelle), jamais un champ de solution (les modèles Pydantic de
    contenu n'incluent que la FORME attendue, jamais la valeur correcte, dans leurs
    messages d'erreur de validation standard)."""
    return [f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in exc.errors()]


# --- API publique (ticket #40 : « Pas forcément routes HTTP ») ------------------------------


def get_question_type(type_id: str) -> QuestionTypeSpec:
    return QUESTION_TYPE_REGISTRY.get(type_id)


def list_question_types() -> list[QuestionTypeSpec]:
    return QUESTION_TYPE_REGISTRY.list_types()


def validate_content(type_id: str, schema_version: int, content_json: dict[str, Any]) -> BaseModel:
    """Valide `content_json` pour `(type_id, schema_version)`. Lève
    `QuestionEngineError` pour un type/une version inconnue, `ContentValidationError`
    pour un contenu structurellement invalide. Retourne le modèle validé (réutilisable
    directement par `public_payload`/`check_answer` sans revalider)."""
    spec = QUESTION_TYPE_REGISTRY.get(type_id)
    _require_schema_version(spec, schema_version)
    try:
        return spec.content_model.model_validate(content_json)
    except ValidationError as exc:
        raise ContentValidationError(_pydantic_errors(exc)) from None


def validate_answer(type_id: str, schema_version: int, answer_json: Any) -> BaseModel:
    spec = QUESTION_TYPE_REGISTRY.get(type_id)
    _require_schema_version(spec, schema_version)
    payload = answer_json if isinstance(answer_json, dict) else {"value": answer_json}
    try:
        return spec.answer_model.model_validate(payload)
    except ValidationError as exc:
        raise ContentValidationError(_pydantic_errors(exc)) from None


def public_payload(
    type_id: str, schema_version: int, content_json: dict[str, Any]
) -> dict[str, Any]:
    """Point d'entrée UNIQUE pour obtenir ce qui peut être envoyé au navigateur — voir
    docstring du module. Revalide toujours `content_json` (défense en profondeur : ne
    fait jamais confiance à un contenu déjà en base sans le repasser par le modèle)."""
    spec = QUESTION_TYPE_REGISTRY.get(type_id)
    content = validate_content(type_id, schema_version, content_json)
    payload = spec.to_public(content)
    payload["type"] = type_id
    payload["requires_ai"] = spec.requires_semantic_correction(content)
    return payload


def check_answer(
    type_id: str,
    schema_version: int,
    content_json: dict[str, Any],
    answer_json: Any,
) -> bool | None:
    """Correction locale déterministe. Retourne `None` si ce contenu précis nécessite une
    correction sémantique (type `SEMANTIC_AI`, ou `HYBRID` sans réponse acceptée locale) —
    à l'appelant (#44) de router vers le fournisseur IA dans ce cas, jamais vers ce
    module."""
    spec = QUESTION_TYPE_REGISTRY.get(type_id)
    content = validate_content(type_id, schema_version, content_json)
    if spec.requires_semantic_correction(content):
        return None
    if spec.check_answer is None:
        return None
    answer = validate_answer(type_id, schema_version, answer_json)
    try:
        return spec.check_answer(content, answer)
    except RequiresSemanticCorrection:
        return None

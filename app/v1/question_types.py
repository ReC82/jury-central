"""Les 26 types de questions du contrat V1 (ticket #40).

Chaque type est défini par deux modèles Pydantic (`*Content`/`*Answer` — Pydantic est
déjà une dépendance du projet via FastAPI, utilisée directement ailleurs, voir
`app/admin.py`/`app/practice.py` : pas de nouveau système de schéma introduit), une
fonction `to_public` qui liste EXPLICITEMENT les champs publics (jamais une copie
amputée des champs privés — voir `docs/question_engine_v1.md`, § Sécurité), et un
`check_answer` (ou `None` pour un type toujours `SEMANTIC_AI`).

Remarque de conception : `QuestionVersion.schema_version` (`app/v1/models.py`, ticket
#38) est déjà la source de vérité pour la version de schéma d'un contenu — aucun champ
`schema_version` n'est dupliqué à l'intérieur de `content_json` lui-même, pour éviter
deux sources de vérité pouvant diverger.

Aucune spécialisation par matière : les mêmes classes servent Informatique, Français, et
toute matière future (voir les tests dédiés `tests/test_ticket40_question_engine.py`,
§ « aucun comportement spécialisé selon subject/module »)."""

import re
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.answer_checking import normalize_text, parse_answer, text_answer_matches
from app.v1.models import AssetKind
from app.v1.question_engine import (
    NO_ASSET,
    QUESTION_TYPE_REGISTRY,
    AssetContract,
    Capability,
    CorrectionMode,
    QuestionTypeSpec,
    SourceDocumentRequirement,
)

_VISUAL_AID_ASSETS = AssetContract(
    allowed_kinds=frozenset({AssetKind.IMAGE, AssetKind.SVG, AssetKind.CHART}),
    min_assets=0,
    max_assets=3,
)


# --- Modèles partagés ------------------------------------------------------------------------


class ChoiceOption(BaseModel):
    option_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    explanation: str = ""


class IdLabel(BaseModel):
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)


def _check_numeric_value(
    *,
    raw_input: str,
    expected_value: float,
    tolerance_abs: float,
    tolerance_rel: float,
    unit: str,
    unit_required: bool,
    submitted_unit: str,
) -> bool:
    """Comparaison numérique tolérante réutilisée par `numeric`/`calculation`/
    `graph_reading` (mode numérique) — jamais de `eval()` (voir `app.answer_checking.
    parse_answer`, basé sur `fractions.Fraction`)."""
    parsed = parse_answer(raw_input)
    if parsed is None:
        return False
    value = float(parsed)
    tolerance = max(tolerance_abs, abs(expected_value) * tolerance_rel)
    if abs(value - expected_value) > tolerance:
        return False
    return not (
        unit_required
        and (not submitted_unit or normalize_text(submitted_unit) != normalize_text(unit))
    )


def _unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} doit contenir des identifiants uniques.")


# =========================================================================================
# 1. multiple_choice — remplace single_choice (voir docstring de app/v1/question_engine.py)
# =========================================================================================


class MultipleChoiceContent(BaseModel):
    prompt: str = Field(min_length=1)
    options: list[ChoiceOption] = Field(min_length=2)
    min_selections: int = Field(default=1, ge=1)
    max_selections: int = Field(default=1, ge=1)
    correct_option_ids: list[str] = Field(min_length=1)
    shuffle: bool = True
    explanation: str = ""

    @model_validator(mode="after")
    def _check(self) -> "MultipleChoiceContent":
        ids = [o.option_id for o in self.options]
        _unique(ids, "option_id")
        if self.min_selections > self.max_selections:
            raise ValueError("min_selections ne peut pas dépasser max_selections.")
        if self.max_selections > len(self.options):
            raise ValueError("max_selections ne peut pas dépasser le nombre d'options.")
        if not (self.min_selections <= len(self.correct_option_ids) <= self.max_selections):
            raise ValueError("correct_option_ids doit respecter min/max_selections.")
        _unique(self.correct_option_ids, "correct_option_ids")
        unknown = set(self.correct_option_ids) - set(ids)
        if unknown:
            raise ValueError(f"correct_option_ids référence un option_id inconnu : {sorted(unknown)}.")
        return self


class MultipleChoiceAnswer(BaseModel):
    selected_option_ids: list[str] = Field(default_factory=list)


def _mc_public(content: MultipleChoiceContent) -> dict[str, Any]:
    return {
        "prompt": content.prompt,
        "options": [{"option_id": o.option_id, "label": o.label} for o in content.options],
        "min_selections": content.min_selections,
        "max_selections": content.max_selections,
        "shuffle": content.shuffle,
    }


def _mc_check(content: MultipleChoiceContent, answer: MultipleChoiceAnswer) -> bool:
    return set(answer.selected_option_ids) == set(content.correct_option_ids)


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="multiple_choice",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.MULTI_SELECT, Capability.LOCAL_GRADING}),
        asset_contract=_VISUAL_AID_ASSETS,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=MultipleChoiceContent,
        answer_model=MultipleChoiceAnswer,
        to_public=_mc_public,
        check_answer=_mc_check,
        description=(
            "Choix parmi 2..N options ; min_selections=max_selections=1 couvre le cas "
            "réponse unique — aucun type single_choice séparé (décision #40)."
        ),
    )
)


# =========================================================================================
# 2. true_false
# =========================================================================================


class TrueFalseContent(BaseModel):
    prompt: str = Field(min_length=1)
    correct_value: bool
    explanation: str = ""


class TrueFalseAnswer(BaseModel):
    value: bool


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="true_false",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.LOCAL_GRADING}),
        asset_contract=_VISUAL_AID_ASSETS,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=TrueFalseContent,
        answer_model=TrueFalseAnswer,
        to_public=lambda c: {"prompt": c.prompt},
        check_answer=lambda c, a: a.value == c.correct_value,
        description=(
            "Type stable conservé séparément de multiple_choice (déjà le cas dans les "
            "vocabulaires existants #17/#23) : vocabulaire Vrai/Faux figé, pas des options "
            "arbitraires — voir décision documentée dans docs/question_engine_v1.md."
        ),
    )
)


# =========================================================================================
# 3. short_answer
# =========================================================================================


class ShortAnswerContent(BaseModel):
    prompt: str = Field(min_length=1)
    accepted_answers: list[str] = Field(default_factory=list)
    rubric: str = ""
    max_length: int = Field(default=200, gt=0)

    @model_validator(mode="after")
    def _check(self) -> "ShortAnswerContent":
        if not self.accepted_answers and not self.rubric.strip():
            raise ValueError("accepted_answers (correction locale) ou rubric (IA) requis.")
        return self

    def requires_semantic(self) -> bool:
        return not self.accepted_answers


class ShortAnswerAnswer(BaseModel):
    text: str = ""


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="short_answer",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.HYBRID,
        capabilities=frozenset({Capability.TEXT_INPUT, Capability.LOCAL_GRADING, Capability.SEMANTIC_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=ShortAnswerContent,
        answer_model=ShortAnswerAnswer,
        to_public=lambda c: {"prompt": c.prompt, "max_length": c.max_length},
        check_answer=lambda c, a: text_answer_matches(c.accepted_answers, a.text),
    )
)


# =========================================================================================
# 4. long_answer
# =========================================================================================


class LongAnswerContent(BaseModel):
    prompt: str = Field(min_length=1)
    rubric: str = Field(min_length=1)
    expected_points: list[str] = Field(default_factory=list)
    # Ticket #73 : 2000 bloquait silencieusement toute réponse rédigée au-delà de ~300
    # mots (constaté en usage réel, Français #47) — 20000 laisse une vraie marge pour un
    # texte argumenté de plusieurs pages, sans risque identifié en aval (DB JSON non
    # bornée, prompt IA non tronqué, export/impression non bornés — voir
    # docs/claude-reports/2026-09-19_ticket-73_long-answer-capacity.md).
    max_length: int = Field(default=20000, gt=0)
    max_score: float = Field(default=1.0, gt=0)
    # Ticket #77 : document de contexte OPTIONNEL. Contrairement à `document_analysis`
    # (analyse OBLIGATOIRE d'un document précis, `SourceDocumentRequirement.REQUIRED`),
    # `long_answer` reste d'abord une question d'expression personnelle — un texte de
    # référence peut l'accompagner sans être une exigence de barème (bug #77 : la
    # question Français id=170 référençait déjà un document dans son contenu, mais ce
    # champ n'existait pas ici, donc Pydantic le supprimait silencieusement et l'élève ne
    # le voyait jamais, alors que le correcteur IA le recevait quand même). S'il est
    # présent, il DOIT être montré à l'élève (`to_public` ci-dessous) — jamais une source
    # cachée.
    source_document_version_id: int | None = Field(default=None, gt=0)


class LongAnswerAnswer(BaseModel):
    text: str = ""


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="long_answer",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.SEMANTIC_AI,
        capabilities=frozenset({Capability.TEXT_INPUT, Capability.SEMANTIC_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.OPTIONAL,
        content_model=LongAnswerContent,
        answer_model=LongAnswerAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "max_length": c.max_length,
            **(
                {"source_document_version_id": c.source_document_version_id}
                if c.source_document_version_id
                else {}
            ),
        },
        check_answer=None,
        description=(
            "Document de contexte optionnel (ticket #77) : jamais une source cachée — "
            "s'il est présent dans le contenu, il est toujours exposé ici."
        ),
    )
)


# =========================================================================================
# 5. fill_blank
# =========================================================================================


class FillBlankSlot(BaseModel):
    blank_id: str = Field(min_length=1)
    accepted_answers: list[str] = Field(min_length=1)


class FillBlankContent(BaseModel):
    text_with_blanks: str = Field(min_length=1)
    blanks: list[FillBlankSlot] = Field(min_length=1)
    explanation: str = ""

    @model_validator(mode="after")
    def _check(self) -> "FillBlankContent":
        _unique([b.blank_id for b in self.blanks], "blank_id")
        referenced = set(re.findall(r"\{\{(\w+)\}\}", self.text_with_blanks))
        declared = {b.blank_id for b in self.blanks}
        if referenced != declared:
            raise ValueError(
                f"les blancs référencés dans text_with_blanks ({sorted(referenced)}) doivent "
                f"correspondre exactement à blanks ({sorted(declared)})."
            )
        return self


class FillBlankAnswer(BaseModel):
    values: dict[str, str] = Field(default_factory=dict)


def _fill_blank_check(content: FillBlankContent, answer: FillBlankAnswer) -> bool:
    return all(
        text_answer_matches(slot.accepted_answers, answer.values.get(slot.blank_id, ""))
        for slot in content.blanks
    )


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="fill_blank",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.TEXT_INPUT, Capability.LOCAL_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=FillBlankContent,
        answer_model=FillBlankAnswer,
        to_public=lambda c: {
            "text_with_blanks": c.text_with_blanks,
            "blank_ids": [b.blank_id for b in c.blanks],
        },
        check_answer=_fill_blank_check,
    )
)


# =========================================================================================
# 6. matching
# =========================================================================================


class MatchingContent(BaseModel):
    prompt: str = Field(min_length=1)
    left_items: list[IdLabel] = Field(min_length=2)
    right_items: list[IdLabel] = Field(min_length=2)
    correct_pairs: dict[str, str] = Field(min_length=1)
    explanation: str = ""

    @model_validator(mode="after")
    def _check(self) -> "MatchingContent":
        left_ids = {i.id for i in self.left_items}
        right_ids = {i.id for i in self.right_items}
        _unique([i.id for i in self.left_items], "left_items.id")
        _unique([i.id for i in self.right_items], "right_items.id")
        if set(self.correct_pairs.keys()) != left_ids:
            raise ValueError("correct_pairs doit couvrir exactement tous les left_items.")
        unknown = set(self.correct_pairs.values()) - right_ids
        if unknown:
            raise ValueError(f"correct_pairs référence un right_item inconnu : {sorted(unknown)}.")
        return self


class MatchingAnswer(BaseModel):
    pairs: dict[str, str] = Field(default_factory=dict)


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="matching",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.DRAG_DROP, Capability.LOCAL_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=MatchingContent,
        answer_model=MatchingAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "left_items": [i.model_dump() for i in c.left_items],
            "right_items": [i.model_dump() for i in c.right_items],
        },
        check_answer=lambda c, a: a.pairs == c.correct_pairs,
    )
)


# =========================================================================================
# 7. classification (réutilise le concept déjà implémenté dans app.editorial_exercise)
# =========================================================================================


class ClassificationContent(BaseModel):
    prompt: str = Field(min_length=1)
    categories: list[str] = Field(min_length=2)
    elements: list[str] = Field(min_length=2)
    correct_categories: list[int]
    explanation: str = ""

    @model_validator(mode="after")
    def _check(self) -> "ClassificationContent":
        if len(self.correct_categories) != len(self.elements):
            raise ValueError("correct_categories doit avoir la même longueur que elements.")
        if any(not (0 <= c < len(self.categories)) for c in self.correct_categories):
            raise ValueError("correct_categories contient un index de catégorie invalide.")
        return self


class ClassificationAnswer(BaseModel):
    assignments: list[int] = Field(default_factory=list)


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="classification",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.DRAG_DROP, Capability.LOCAL_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=ClassificationContent,
        answer_model=ClassificationAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "categories": c.categories,
            "elements": c.elements,
        },
        check_answer=lambda c, a: a.assignments == c.correct_categories,
        description="Catégories et éléments en nombre variable (pas limité à 2/3 catégories).",
    )
)


# =========================================================================================
# 8. ordering
# =========================================================================================


class OrderingContent(BaseModel):
    prompt: str = Field(min_length=1)
    items: list[IdLabel] = Field(min_length=2)
    correct_order: list[str]
    explanation: str = ""

    @model_validator(mode="after")
    def _check(self) -> "OrderingContent":
        ids = [i.id for i in self.items]
        _unique(ids, "items.id")
        if sorted(self.correct_order) != sorted(ids):
            raise ValueError("correct_order doit être une permutation des identifiants de items.")
        return self


class OrderingAnswer(BaseModel):
    order: list[str] = Field(default_factory=list)


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="ordering",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.ORDERABLE, Capability.LOCAL_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=OrderingContent,
        answer_model=OrderingAnswer,
        to_public=lambda c: {"prompt": c.prompt, "items": [i.model_dump() for i in c.items]},
        check_answer=lambda c, a: a.order == c.correct_order,
    )
)


# =========================================================================================
# 9. numeric
# =========================================================================================


class NumericContent(BaseModel):
    prompt: str = Field(min_length=1)
    expected_value: float
    tolerance_abs: float = Field(default=0.0, ge=0)
    tolerance_rel: float = Field(default=0.0, ge=0)
    unit: str = ""
    unit_required: bool = False
    explanation: str = ""


class NumericAnswer(BaseModel):
    raw_input: str = ""
    unit: str = ""


def _numeric_check(content: NumericContent, answer: NumericAnswer) -> bool:
    return _check_numeric_value(
        raw_input=answer.raw_input,
        expected_value=content.expected_value,
        tolerance_abs=content.tolerance_abs,
        tolerance_rel=content.tolerance_rel,
        unit=content.unit,
        unit_required=content.unit_required,
        submitted_unit=answer.unit,
    )


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="numeric",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.TEXT_INPUT, Capability.LOCAL_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=NumericContent,
        answer_model=NumericAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "unit": c.unit,
            "unit_required": c.unit_required,
        },
        check_answer=_numeric_check,
    )
)


# =========================================================================================
# 10. diagnostic
# =========================================================================================


class DiagnosticContent(BaseModel):
    prompt: str = Field(min_length=1)
    rubric: str = Field(min_length=1)
    expected_points: list[str] = Field(default_factory=list)
    critical_points: list[str] = Field(default_factory=list)
    # Ticket #73 : avant ce champ, ce type n'exposait aucun `max_length` — le template
    # retombait sur un plafond de 2000 caractères codé en dur
    # (`app/templates/v1_session_question.html`), bloquant silencieusement toute réponse
    # plus longue. Explicite désormais, comme `long_answer`.
    max_length: int = Field(default=20000, gt=0)
    max_score: float = Field(default=1.0, gt=0)


class DiagnosticAnswer(BaseModel):
    text: str = ""


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="diagnostic",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.SEMANTIC_AI,
        capabilities=frozenset({Capability.TEXT_INPUT, Capability.SEMANTIC_GRADING}),
        asset_contract=_VISUAL_AID_ASSETS,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=DiagnosticContent,
        answer_model=DiagnosticAnswer,
        to_public=lambda c: {"prompt": c.prompt, "max_length": c.max_length},
        check_answer=None,
    )
)


# =========================================================================================
# 11. procedure
# =========================================================================================


class ProcedureContent(BaseModel):
    prompt: str = Field(min_length=1)
    rubric: str = Field(min_length=1)
    expected_steps: list[str] = Field(default_factory=list)
    # Ticket #73 : voir DiagnosticContent.max_length, même correctif.
    max_length: int = Field(default=20000, gt=0)
    max_score: float = Field(default=1.0, gt=0)


class ProcedureAnswer(BaseModel):
    text: str = ""


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="procedure",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.SEMANTIC_AI,
        capabilities=frozenset({Capability.TEXT_INPUT, Capability.SEMANTIC_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=ProcedureContent,
        answer_model=ProcedureAnswer,
        to_public=lambda c: {"prompt": c.prompt, "max_length": c.max_length},
        check_answer=None,
    )
)


# =========================================================================================
# 12. vocabulary
# =========================================================================================


class VocabularyContent(BaseModel):
    prompt: str = Field(min_length=1)
    direction: Literal["term_to_definition", "definition_to_term"] = "term_to_definition"
    accepted_answers: list[str] = Field(default_factory=list)
    rubric: str = ""

    @model_validator(mode="after")
    def _check(self) -> "VocabularyContent":
        if not self.accepted_answers and not self.rubric.strip():
            raise ValueError("accepted_answers (correction locale) ou rubric (IA) requis.")
        return self

    def requires_semantic(self) -> bool:
        return not self.accepted_answers


class VocabularyAnswer(BaseModel):
    text: str = ""


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="vocabulary",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.HYBRID,
        capabilities=frozenset({Capability.TEXT_INPUT, Capability.LOCAL_GRADING, Capability.SEMANTIC_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=VocabularyContent,
        answer_model=VocabularyAnswer,
        to_public=lambda c: {"prompt": c.prompt, "direction": c.direction},
        check_answer=lambda c, a: text_answer_matches(c.accepted_answers, a.text),
        description="Pas spécifique à l'Informatique — terme↔définition, toute matière.",
    )
)


# =========================================================================================
# 13. calculation
# =========================================================================================


class CalculationContent(BaseModel):
    prompt: str = Field(min_length=1)
    expected_value: float
    tolerance_abs: float = Field(default=0.0, ge=0)
    tolerance_rel: float = Field(default=0.0, ge=0)
    unit: str = ""
    unit_required: bool = False
    rubric: str = ""  # facultatif : grille de correction pour un examen de la démarche future (#45)


class CalculationAnswer(BaseModel):
    raw_input: str = ""
    unit: str = ""


def _calculation_check(content: CalculationContent, answer: CalculationAnswer) -> bool:
    return _check_numeric_value(
        raw_input=answer.raw_input,
        expected_value=content.expected_value,
        tolerance_abs=content.tolerance_abs,
        tolerance_rel=content.tolerance_rel,
        unit=content.unit,
        unit_required=content.unit_required,
        submitted_unit=answer.unit,
    )


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="calculation",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.TEXT_INPUT, Capability.LOCAL_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=CalculationContent,
        answer_model=CalculationAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "unit": c.unit,
            "unit_required": c.unit_required,
        },
        check_answer=_calculation_check,
        description="Distinct de numeric par intention pédagogique (calcul à mener) ; même mécanique de comparaison tolérante.",
    )
)


# =========================================================================================
# 14. formula
# =========================================================================================


class FormulaContent(BaseModel):
    prompt: str = Field(min_length=1)
    accepted_representations: list[str] = Field(default_factory=list)
    rubric: str = ""
    render_hint: Literal["plain", "latex"] = "latex"

    @model_validator(mode="after")
    def _check(self) -> "FormulaContent":
        if not self.accepted_representations and not self.rubric.strip():
            raise ValueError("accepted_representations (local) ou rubric (IA) requis.")
        return self

    def requires_semantic(self) -> bool:
        return not self.accepted_representations


class FormulaAnswer(BaseModel):
    text: str = ""


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="formula",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.HYBRID,
        capabilities=frozenset({Capability.FORMULA, Capability.TEXT_INPUT, Capability.LOCAL_GRADING, Capability.SEMANTIC_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=FormulaContent,
        answer_model=FormulaAnswer,
        to_public=lambda c: {"prompt": c.prompt, "render_hint": c.render_hint},
        check_answer=lambda c, a: text_answer_matches(c.accepted_representations, a.text),
        description="Comparaison textuelle normalisée uniquement — jamais d'évaluation mathématique de code. Rendu LaTeX/KaTeX repoussé.",
    )
)


# =========================================================================================
# 15. graph_reading — response_mode plutôt que des sous-types (composition, voir ticket)
# =========================================================================================


class GraphReadingContent(BaseModel):
    prompt: str = Field(min_length=1)
    graph_config: dict[str, Any] = Field(default_factory=dict)
    response_mode: Literal["numeric", "text", "multiple_choice"] = "numeric"
    expected_value: float | None = None
    tolerance_abs: float = Field(default=0.0, ge=0)
    tolerance_rel: float = Field(default=0.0, ge=0)
    unit: str = ""
    unit_required: bool = False
    accepted_answers: list[str] = Field(default_factory=list)
    rubric: str = ""
    options: list[ChoiceOption] = Field(default_factory=list)
    correct_option_ids: list[str] = Field(default_factory=list)
    min_selections: int = Field(default=1, ge=1)
    max_selections: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def _check(self) -> "GraphReadingContent":
        if self.response_mode == "numeric" and self.expected_value is None:
            raise ValueError("expected_value requis pour response_mode=numeric.")
        if self.response_mode == "text" and not self.accepted_answers and not self.rubric.strip():
            raise ValueError("accepted_answers ou rubric requis pour response_mode=text.")
        if self.response_mode == "multiple_choice":
            ids = [o.option_id for o in self.options]
            _unique(ids, "options.option_id")
            if len(self.options) < 2:
                raise ValueError("au moins deux options requises pour response_mode=multiple_choice.")
            unknown = set(self.correct_option_ids) - set(ids)
            if unknown or not self.correct_option_ids:
                raise ValueError("correct_option_ids invalide pour response_mode=multiple_choice.")
        return self

    def requires_semantic(self) -> bool:
        return self.response_mode == "text" and not self.accepted_answers


class GraphReadingAnswer(BaseModel):
    raw_input: str = ""
    unit: str = ""
    text: str = ""
    selected_option_ids: list[str] = Field(default_factory=list)


def _graph_reading_check(content: GraphReadingContent, answer: GraphReadingAnswer) -> bool:
    if content.response_mode == "numeric":
        return _check_numeric_value(
            raw_input=answer.raw_input,
            expected_value=content.expected_value or 0.0,
            tolerance_abs=content.tolerance_abs,
            tolerance_rel=content.tolerance_rel,
            unit=content.unit,
            unit_required=content.unit_required,
            submitted_unit=answer.unit,
        )
    if content.response_mode == "multiple_choice":
        return set(answer.selected_option_ids) == set(content.correct_option_ids)
    return text_answer_matches(content.accepted_answers, answer.text)


def _graph_reading_public(content: GraphReadingContent) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "prompt": content.prompt,
        "graph_config": content.graph_config,
        "response_mode": content.response_mode,
    }
    if content.response_mode == "numeric":
        payload["unit"] = content.unit
        payload["unit_required"] = content.unit_required
    elif content.response_mode == "multiple_choice":
        payload["options"] = [{"option_id": o.option_id, "label": o.label} for o in content.options]
        payload["min_selections"] = content.min_selections
        payload["max_selections"] = content.max_selections
    return payload


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="graph_reading",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.HYBRID,
        capabilities=frozenset({Capability.GRAPH, Capability.TEXT_INPUT, Capability.LOCAL_GRADING, Capability.SEMANTIC_GRADING}),
        asset_contract=AssetContract(
            allowed_kinds=frozenset({AssetKind.IMAGE, AssetKind.SVG, AssetKind.CHART}), min_assets=0, max_assets=2
        ),
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=GraphReadingContent,
        answer_model=GraphReadingAnswer,
        to_public=_graph_reading_public,
        check_answer=_graph_reading_check,
        description="Lecture seule d'un graphique ; réponse numérique/texte/choix selon response_mode (composition, pas un sous-type par forme de réponse).",
    )
)


# =========================================================================================
# 16. graph_interaction
# =========================================================================================


class GraphPoint(BaseModel):
    x: float
    y: float


class GraphInteractionContent(BaseModel):
    prompt: str = Field(min_length=1)
    graph_config: dict[str, Any] = Field(default_factory=dict)
    interaction_kind: Literal["point_placement", "curve_trace", "parameter_set"] = "point_placement"
    expected_points: list[GraphPoint] = Field(default_factory=list)
    point_tolerance: float = Field(default=0.1, ge=0)
    expected_parameters: dict[str, float] = Field(default_factory=dict)
    parameter_tolerance: float = Field(default=0.05, ge=0)


class GraphInteractionAnswer(BaseModel):
    points: list[GraphPoint] = Field(default_factory=list)
    parameters: dict[str, float] = Field(default_factory=dict)


def _graph_interaction_check(content: GraphInteractionContent, answer: GraphInteractionAnswer) -> bool:
    if content.interaction_kind == "parameter_set":
        if set(answer.parameters.keys()) != set(content.expected_parameters.keys()):
            return False
        return all(
            abs(answer.parameters[key] - value) <= content.parameter_tolerance
            for key, value in content.expected_parameters.items()
        )
    if len(answer.points) != len(content.expected_points):
        return False
    remaining = list(answer.points)
    for expected in content.expected_points:
        match = next(
            (
                p
                for p in remaining
                if abs(p.x - expected.x) <= content.point_tolerance
                and abs(p.y - expected.y) <= content.point_tolerance
            ),
            None,
        )
        if match is None:
            return False
        remaining.remove(match)
    return True


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="graph_interaction",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.GRAPH, Capability.DRAG_DROP, Capability.LOCAL_GRADING}),
        asset_contract=AssetContract(
            allowed_kinds=frozenset({AssetKind.IMAGE, AssetKind.SVG, AssetKind.CHART}), min_assets=0, max_assets=2
        ),
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=GraphInteractionContent,
        answer_model=GraphInteractionAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "graph_config": c.graph_config,
            "interaction_kind": c.interaction_kind,
        },
        check_answer=_graph_interaction_check,
        description="Points placés/paramètres, comparés avec tolérance — pas de renderer complet dans ce ticket.",
    )
)


# =========================================================================================
# 17. diagram_labeling — exemple du ticket : IMAGE + DRAG_DROP + LOCAL_GRADING
# =========================================================================================


class DiagramZone(BaseModel):
    zone_id: str = Field(min_length=1)
    marker: str = ""


class DiagramLabelingContent(BaseModel):
    prompt: str = Field(min_length=1)
    zones: list[DiagramZone] = Field(min_length=1)
    label_options: list[IdLabel] = Field(min_length=1)
    correct_mapping: dict[str, str] = Field(min_length=1)

    @model_validator(mode="after")
    def _check(self) -> "DiagramLabelingContent":
        zone_ids = {z.zone_id for z in self.zones}
        label_ids = {label.id for label in self.label_options}
        _unique([z.zone_id for z in self.zones], "zones.zone_id")
        if set(self.correct_mapping.keys()) != zone_ids:
            raise ValueError("correct_mapping doit couvrir exactement toutes les zones.")
        unknown = set(self.correct_mapping.values()) - label_ids
        if unknown:
            raise ValueError(f"correct_mapping référence un label_id inconnu : {sorted(unknown)}.")
        return self


class DiagramLabelingAnswer(BaseModel):
    mapping: dict[str, str] = Field(default_factory=dict)


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="diagram_labeling",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.IMAGE, Capability.DRAG_DROP, Capability.LOCAL_GRADING}),
        asset_contract=AssetContract(allowed_kinds=frozenset({AssetKind.IMAGE, AssetKind.SVG}), min_assets=1, max_assets=1),
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=DiagramLabelingContent,
        answer_model=DiagramLabelingAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "zones": [z.model_dump() for z in c.zones],
            "label_options": [label.model_dump() for label in c.label_options],
        },
        check_answer=lambda c, a: a.mapping == c.correct_mapping,
    )
)


# =========================================================================================
# 18. image_identification
# =========================================================================================


class ImageIdentificationContent(BaseModel):
    prompt: str = Field(min_length=1)
    response_mode: Literal["choice", "text"] = "choice"
    options: list[ChoiceOption] = Field(default_factory=list)
    correct_option_ids: list[str] = Field(default_factory=list)
    accepted_answers: list[str] = Field(default_factory=list)
    rubric: str = ""

    @model_validator(mode="after")
    def _check(self) -> "ImageIdentificationContent":
        if self.response_mode == "choice":
            ids = [o.option_id for o in self.options]
            _unique(ids, "options.option_id")
            if len(self.options) < 2:
                raise ValueError("au moins deux options requises pour response_mode=choice.")
            if not self.correct_option_ids or set(self.correct_option_ids) - set(ids):
                raise ValueError("correct_option_ids invalide pour response_mode=choice.")
        elif not self.accepted_answers and not self.rubric.strip():
            raise ValueError("accepted_answers ou rubric requis pour response_mode=text.")
        return self

    def requires_semantic(self) -> bool:
        return self.response_mode == "text" and not self.accepted_answers


class ImageIdentificationAnswer(BaseModel):
    selected_option_ids: list[str] = Field(default_factory=list)
    text: str = ""


def _image_identification_check(content: ImageIdentificationContent, answer: ImageIdentificationAnswer) -> bool:
    if content.response_mode == "choice":
        return set(answer.selected_option_ids) == set(content.correct_option_ids)
    return text_answer_matches(content.accepted_answers, answer.text)


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="image_identification",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.HYBRID,
        capabilities=frozenset({Capability.IMAGE, Capability.TEXT_INPUT, Capability.MULTI_SELECT, Capability.LOCAL_GRADING, Capability.SEMANTIC_GRADING}),
        asset_contract=AssetContract(allowed_kinds=frozenset({AssetKind.IMAGE}), min_assets=1, max_assets=1),
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=ImageIdentificationContent,
        answer_model=ImageIdentificationAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "response_mode": c.response_mode,
            "options": [{"option_id": o.option_id, "label": o.label} for o in c.options],
        },
        check_answer=_image_identification_check,
        description="Asset image requis (voir asset_contract).",
    )
)


# =========================================================================================
# 19. hotspot
# =========================================================================================


class HotspotZone(BaseModel):
    zone_id: str = Field(min_length=1)
    x_min: float = Field(ge=0, le=1)
    y_min: float = Field(ge=0, le=1)
    x_max: float = Field(ge=0, le=1)
    y_max: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def _check(self) -> "HotspotZone":
        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            raise ValueError("x_min/y_min doivent être strictement inférieurs à x_max/y_max.")
        return self


class HotspotContent(BaseModel):
    prompt: str = Field(min_length=1)
    zones: list[HotspotZone] = Field(min_length=1)
    correct_zone_ids: list[str] = Field(min_length=1)
    min_selections: int = Field(default=1, ge=1)
    max_selections: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def _check_mapping(self) -> "HotspotContent":
        zone_ids = {z.zone_id for z in self.zones}
        _unique([z.zone_id for z in self.zones], "zones.zone_id")
        unknown = set(self.correct_zone_ids) - zone_ids
        if unknown:
            raise ValueError(f"correct_zone_ids référence une zone inconnue : {sorted(unknown)}.")
        return self


class HotspotAnswer(BaseModel):
    selected_zone_ids: list[str] = Field(default_factory=list)
    normalized_points: list[tuple[float, float]] = Field(default_factory=list)


def _resolve_hotspot_zone_ids(content: HotspotContent, answer: HotspotAnswer) -> set[str]:
    """Préfère les identifiants de zone explicites (recommandé, voir docstring du
    ticket) ; à défaut, résout des points normalisés par containment dans les
    rectangles définis par le contenu — jamais une correction « au pixel » sans zones
    déclarées."""
    if answer.selected_zone_ids:
        return set(answer.selected_zone_ids)
    resolved: set[str] = set()
    for x, y in answer.normalized_points:
        for zone in content.zones:
            if zone.x_min <= x <= zone.x_max and zone.y_min <= y <= zone.y_max:
                resolved.add(zone.zone_id)
    return resolved


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="hotspot",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.IMAGE, Capability.HOTSPOT, Capability.LOCAL_GRADING}),
        asset_contract=AssetContract(allowed_kinds=frozenset({AssetKind.IMAGE, AssetKind.SVG}), min_assets=1, max_assets=1),
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=HotspotContent,
        answer_model=HotspotAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "zones": [z.model_dump() for z in c.zones],
            "min_selections": c.min_selections,
            "max_selections": c.max_selections,
        },
        check_answer=lambda c, a: _resolve_hotspot_zone_ids(c, a) == set(c.correct_zone_ids),
        description="IDs de zone préférés à une correction approximative par pixels (voir ticket).",
    )
)


# =========================================================================================
# 20. table_completion
# =========================================================================================


class TableCell(BaseModel):
    cell_id: str = Field(min_length=1)
    editable: bool = False
    value: str = ""


class TableCompletionContent(BaseModel):
    prompt: str = Field(min_length=1)
    headers: list[str] = Field(min_length=1)
    rows: list[list[TableCell]] = Field(min_length=1)
    accepted_answers: dict[str, list[str]] = Field(default_factory=dict)
    rubric: str = ""

    @model_validator(mode="after")
    def _check(self) -> "TableCompletionContent":
        all_ids = [cell.cell_id for row in self.rows for cell in row]
        _unique(all_ids, "cell_id")
        return self

    def _editable_ids(self) -> set[str]:
        return {cell.cell_id for row in self.rows for cell in row if cell.editable}

    def requires_semantic(self) -> bool:
        """IA nécessaire dès qu'au moins une cellule éditable n'a pas de réponse
        acceptée localement — pas de correction locale partielle sur un sous-ensemble
        de cellules dans ce ticket."""
        return bool(self._editable_ids() - set(self.accepted_answers.keys()))


class TableCompletionAnswer(BaseModel):
    values: dict[str, str] = Field(default_factory=dict)


def _table_completion_check(content: TableCompletionContent, answer: TableCompletionAnswer) -> bool:
    return all(
        text_answer_matches(content.accepted_answers.get(cell_id, []), answer.values.get(cell_id, ""))
        for cell_id in content._editable_ids()
    )


def _table_completion_public(content: TableCompletionContent) -> dict[str, Any]:
    return {
        "prompt": content.prompt,
        "headers": content.headers,
        "rows": [
            [
                {"cell_id": cell.cell_id, "editable": cell.editable, "value": "" if cell.editable else cell.value}
                for cell in row
            ]
            for row in content.rows
        ],
    }


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="table_completion",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.HYBRID,
        capabilities=frozenset({Capability.TABLE, Capability.TEXT_INPUT, Capability.LOCAL_GRADING, Capability.SEMANTIC_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=TableCompletionContent,
        answer_model=TableCompletionAnswer,
        to_public=_table_completion_public,
        check_answer=_table_completion_check,
    )
)


# =========================================================================================
# 21. document_analysis — priorité Français
# =========================================================================================


class DocumentAnalysisContent(BaseModel):
    prompt: str = Field(min_length=1)
    source_document_version_id: int = Field(gt=0)
    rubric: str = Field(min_length=1)
    expected_points: list[str] = Field(default_factory=list)
    # Ticket #73 : voir DiagnosticContent.max_length, même correctif — prioritaire pour
    # Français (analyse de document en réponse rédigée).
    max_length: int = Field(default=20000, gt=0)
    max_score: float = Field(default=1.0, gt=0)


class DocumentAnalysisAnswer(BaseModel):
    text: str = ""


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="document_analysis",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.SEMANTIC_AI,
        capabilities=frozenset({Capability.DOCUMENT, Capability.TEXT_INPUT, Capability.SEMANTIC_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.REQUIRED,
        content_model=DocumentAnalysisContent,
        answer_model=DocumentAnalysisAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "source_document_version_id": c.source_document_version_id,
            "max_length": c.max_length,
        },
        check_answer=None,
        description="Référence toujours une SourceDocumentVersion — jamais de texte dupliqué dans content_json.",
    )
)


# =========================================================================================
# 22. source_comparison
# =========================================================================================


class SourceComparisonContent(BaseModel):
    prompt: str = Field(min_length=1)
    source_document_version_ids: list[int] = Field(min_length=2)
    rubric: str = Field(min_length=1)
    expected_points: list[str] = Field(default_factory=list)
    # Ticket #73 : voir DiagnosticContent.max_length, même correctif — prioritaire pour
    # Français (comparaison de sources en réponse rédigée).
    max_length: int = Field(default=20000, gt=0)
    max_score: float = Field(default=1.0, gt=0)

    @model_validator(mode="after")
    def _check(self) -> "SourceComparisonContent":
        if any(v <= 0 for v in self.source_document_version_ids):
            raise ValueError("source_document_version_ids doit contenir des identifiants positifs.")
        _unique([str(v) for v in self.source_document_version_ids], "source_document_version_ids")
        return self


class SourceComparisonAnswer(BaseModel):
    text: str = ""


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="source_comparison",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.SEMANTIC_AI,
        capabilities=frozenset({Capability.DOCUMENT, Capability.TEXT_INPUT, Capability.SEMANTIC_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.MULTIPLE,
        content_model=SourceComparisonContent,
        answer_model=SourceComparisonAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "source_document_version_ids": c.source_document_version_ids,
            "max_length": c.max_length,
        },
        check_answer=None,
    )
)


# =========================================================================================
# 23. timeline
# =========================================================================================


class TimelineContent(BaseModel):
    prompt: str = Field(min_length=1)
    events: list[IdLabel] = Field(min_length=2)
    correct_order: list[str]
    explanation: str = ""

    @model_validator(mode="after")
    def _check(self) -> "TimelineContent":
        ids = [e.id for e in self.events]
        _unique(ids, "events.id")
        if sorted(self.correct_order) != sorted(ids):
            raise ValueError("correct_order doit être une permutation des identifiants de events.")
        return self


class TimelineAnswer(BaseModel):
    order: list[str] = Field(default_factory=list)


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="timeline",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.LOCAL,
        capabilities=frozenset({Capability.ORDERABLE, Capability.LOCAL_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=TimelineContent,
        answer_model=TimelineAnswer,
        to_public=lambda c: {"prompt": c.prompt, "events": [e.model_dump() for e in c.events]},
        check_answer=lambda c, a: a.order == c.correct_order,
    )
)


# =========================================================================================
# 24. code_reading — jamais d'exécution du code utilisateur ou du stimulus
# =========================================================================================


class CodeReadingContent(BaseModel):
    prompt: str = Field(min_length=1)
    language: str = "text"
    code: str = Field(min_length=1)
    response_mode: Literal["choice", "text"] = "choice"
    options: list[ChoiceOption] = Field(default_factory=list)
    correct_option_ids: list[str] = Field(default_factory=list)
    accepted_answers: list[str] = Field(default_factory=list)
    rubric: str = ""

    @model_validator(mode="after")
    def _check(self) -> "CodeReadingContent":
        if self.response_mode == "choice":
            ids = [o.option_id for o in self.options]
            _unique(ids, "options.option_id")
            if len(self.options) < 2 or not self.correct_option_ids:
                raise ValueError("options/correct_option_ids invalides pour response_mode=choice.")
        elif not self.accepted_answers and not self.rubric.strip():
            raise ValueError("accepted_answers ou rubric requis pour response_mode=text.")
        return self

    def requires_semantic(self) -> bool:
        return self.response_mode == "text" and not self.accepted_answers


class CodeReadingAnswer(BaseModel):
    selected_option_ids: list[str] = Field(default_factory=list)
    text: str = ""


def _code_reading_check(content: CodeReadingContent, answer: CodeReadingAnswer) -> bool:
    if content.response_mode == "choice":
        return set(answer.selected_option_ids) == set(content.correct_option_ids)
    return text_answer_matches(content.accepted_answers, answer.text)


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="code_reading",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.HYBRID,
        capabilities=frozenset({Capability.CODE, Capability.TEXT_INPUT, Capability.LOCAL_GRADING, Capability.SEMANTIC_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=CodeReadingContent,
        answer_model=CodeReadingAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "language": c.language,
            "code": c.code,
            "response_mode": c.response_mode,
            "options": [{"option_id": o.option_id, "label": o.label} for o in c.options],
        },
        check_answer=_code_reading_check,
        description="Le code est un stimulus affiché, jamais exécuté (contrat V1).",
    )
)


# =========================================================================================
# 25. code_completion — jamais d'exécution
# =========================================================================================


class CodeCompletionContent(BaseModel):
    prompt: str = Field(min_length=1)
    language: str = "text"
    code_stimulus: str = Field(min_length=1)
    accepted_answers: list[str] = Field(default_factory=list)
    rubric: str = ""

    @model_validator(mode="after")
    def _check(self) -> "CodeCompletionContent":
        if not self.accepted_answers and not self.rubric.strip():
            raise ValueError("accepted_answers (local) ou rubric (IA) requis.")
        return self

    def requires_semantic(self) -> bool:
        return not self.accepted_answers


class CodeCompletionAnswer(BaseModel):
    text: str = ""


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="code_completion",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.HYBRID,
        capabilities=frozenset({Capability.CODE, Capability.TEXT_INPUT, Capability.LOCAL_GRADING, Capability.SEMANTIC_GRADING}),
        asset_contract=NO_ASSET,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=CodeCompletionContent,
        answer_model=CodeCompletionAnswer,
        to_public=lambda c: {
            "prompt": c.prompt,
            "language": c.language,
            "code_stimulus": c.code_stimulus,
        },
        check_answer=lambda c, a: text_answer_matches(c.accepted_answers, a.text),
        description="Complétion textuelle d'un extrait — jamais d'exécution arbitraire (contrat V1).",
    )
)


# =========================================================================================
# 26. troubleshooting
# =========================================================================================


class TroubleshootingContent(BaseModel):
    prompt: str = Field(min_length=1)
    rubric: str = Field(min_length=1)
    expected_points: list[str] = Field(default_factory=list)
    critical_points: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)
    # Ticket #73 : voir DiagnosticContent.max_length, même correctif.
    max_length: int = Field(default=20000, gt=0)
    max_score: float = Field(default=1.0, gt=0)


class TroubleshootingAnswer(BaseModel):
    text: str = ""


QUESTION_TYPE_REGISTRY.register(
    QuestionTypeSpec(
        type_id="troubleshooting",
        schema_versions=frozenset({1}),
        correction_mode=CorrectionMode.SEMANTIC_AI,
        capabilities=frozenset({Capability.TEXT_INPUT, Capability.SEMANTIC_GRADING}),
        asset_contract=_VISUAL_AID_ASSETS,
        source_document_requirement=SourceDocumentRequirement.NONE,
        content_model=TroubleshootingContent,
        answer_model=TroubleshootingAnswer,
        to_public=lambda c: {"prompt": c.prompt, "max_length": c.max_length},
        check_answer=None,
    )
)

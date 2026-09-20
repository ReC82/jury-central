"""Structures de données — Examen blanc CESS Français (nouveau chantier, mode Examen
blanc, priorité absolue).

Contrat SÉPARÉ du contrat « questionnaire » générique (#23) : un examen blanc n'est pas
une liste de questions indépendantes notées 0-1, mais UNE production longue unique, notée
holistiquement sur 100 via une grille structurée en catégories (A/B/C/D pour la synthèse,
A/B/C pour l'argumentation). Même discipline que le reste du moteur IA (`app.ai.schemas`) :
dataclasses simples, jamais de texte libre non structuré échangé avec le fournisseur IA."""

from dataclasses import dataclass, field

EXAM_TYPES = ("synthesis", "argumentation_opinion", "argumentation_request")

# Types de documents (§ 7 du chantier) — jamais 3 fois le même angle.
DOCUMENT_KINDS = ("faits_donnees", "expert_analyse", "temoignage_chronique")


@dataclass(frozen=True)
class MockExamGenerationRequest:
    """Entrée de `generate_french_mock_exam`. `theme` est choisi CÔTÉ SERVEUR
    (`app.v1.french_mock_exam_service.choose_theme`, § 30 du chantier : anti-répétition
    fiable, jamais dépendante du bon respect d'une consigne texte par le modèle) — l'IA
    écrit les documents sur ce thème, elle ne le choisit pas elle-même. `avoid_task_
    signatures` (§ 3) reste transmis en texte : contrairement au thème, l'angle exact
    d'une tâche n'a pas de liste fermée côté serveur."""

    exam_type: str
    theme: str
    min_words: int
    max_words: int
    avoid_task_signatures: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.exam_type not in EXAM_TYPES:
            raise ValueError(f"exam_type inconnu : {self.exam_type!r}.")
        if not self.theme.strip():
            raise ValueError("theme requis.")
        if self.min_words <= 0 or self.max_words < self.min_words:
            raise ValueError("min_words/max_words incohérents.")


@dataclass
class MockExamDocument:
    title: str
    doc_kind: str
    text: str


@dataclass
class MockExamRubricCategory:
    name: str
    max_points: float
    criteria: list[str] = field(default_factory=list)


@dataclass
class MockExamKeyIdea:
    """Élément du corrigé PRIVÉ (§ 16 du chantier) — jamais rendu au navigateur avant
    correction. `source_document_indexes` : 1-based, référence les documents générés dans
    l'ordre (1, 2, 3)."""

    idea: str
    source_document_indexes: list[int] = field(default_factory=list)
    axis: str = ""


@dataclass
class MockExamGeneration:
    """Sortie de `generate_french_mock_exam` : exactement 3 documents (§ 5), une tâche
    créée APRÈS les documents (§ 9), une grille /100 structurée, et un corrigé privé
    (§ 16/§ 24) jamais exposé à l'élève avant correction. `theme`/`theme_key` ne sont PAS
    renvoyés par l'IA : ils sont déjà connus côté serveur (choisis avant l'appel, voir
    `MockExamGenerationRequest.theme`), jamais laissés dériver de la réponse du modèle."""

    documents: list[MockExamDocument] = field(default_factory=list)
    task_prompt: str = ""
    rubric_categories: list[MockExamRubricCategory] = field(default_factory=list)
    key_ideas: list[MockExamKeyIdea] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    complements: list[str] = field(default_factory=list)
    # Argumentation uniquement (listes vides pour une synthèse) — § 19/§ 21 du chantier.
    target_opinion: str = ""
    required_genre: str = ""
    recipient: str = ""


@dataclass
class MockExamCategoryScore:
    name: str
    points: float
    max_points: float
    comment: str = ""


@dataclass
class MockExamCorrection:
    """Sortie de `correct_french_mock_exam` — § 38/§ 39/§ 40 du chantier (feedback détaillé
    générique + spécifique au type d'épreuve)."""

    score: float
    max_score: float
    category_scores: list[MockExamCategoryScore] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    structure_feedback: str = ""
    document_comprehension_feedback: str = ""
    source_usage_feedback: str = ""
    task_specific_feedback: str = ""
    language_feedback: str = ""
    length_feedback: str = ""

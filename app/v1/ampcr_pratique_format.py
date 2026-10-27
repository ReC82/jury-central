"""Format d'un exercice pratique écrit AMPCR (ticket #192).

L'épreuve pratique se fait « UNIQUEMENT PAR ÉCRIT » (consignes 2026-2027/1, p. 3) : un
exercice décrit une situation de technicien, fournit les documents nécessaires (tableau,
relevé, schéma) et demande une réponse rédigée, corrigée selon un barème explicite.

Pas de nouveau moteur : `to_question_content` produit le contenu d'un type existant —
`document_analysis` si l'exercice a des documents (enregistrés via
`app.v1.models.create_source_document`), sinon `long_answer` — que les sessions, la
correction IA batch, l'historique et l'impression traitent déjà. Le barème devient la
`rubric`, les attendus `expected_points`, le total `max_score`.

`validate_exercise` refuse ce que le ticket interdit : consigne implicite, barème vide,
exigence inconnue, question de développé d'acronyme, faux sujet « officiel ».
"""

import re
from dataclasses import dataclass

from app.v1.ampcr_pratique_plan import REQUIREMENTS_BY_ID
from app.v1.ampcr_pratique_visuals import T568B, Figure, connector_pins_svg
from app.v1.question_types import QUESTION_TYPE_REGISTRY


@dataclass(frozen=True)
class ExerciseDocument:
    title: str
    kind: str  # "texte" | "tableau" | "schéma" | "console" (terminal, journal — ticket #194)
    content_text: str
    # Ticket #230 : schéma servi en fichier statique (chemin sous `app/static/`), affiché dans
    # la question ; `content_text` en reste la description textuelle complète.
    image: str = ""

    def table_rows(self) -> list[list[str]]:
        """Lignes d'un document « tableau » écrit en Markdown (`| a | b |`), séparateur exclu."""
        rows = []
        for line in self.content_text.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and not all(set(c) <= {"-", ":"} for c in cells):
                rows.append(cells)
        return rows


@dataclass(frozen=True)
class ScoringCriterion:
    label: str
    points: float
    expected: str  # ce qui doit figurer dans la réponse pour obtenir les points


@dataclass(frozen=True)
class PracticalExercise:
    code: str
    title: str
    requirement_ids: tuple[str, ...]
    context: str
    documents: tuple[ExerciseDocument, ...]
    instructions: tuple[str, ...]  # consignes numérotées, chacune explicite
    criteria: tuple[ScoringCriterion, ...]
    justified_correction: str
    calculator_needed: bool = False

    @property
    def total_points(self) -> float:
        return sum(c.points for c in self.criteria)

    @property
    def question_type(self) -> str:
        return "document_analysis" if self.documents else "long_answer"


MIN_CONTEXT_LENGTH = 80

_ACRONYM_EXPANSION_RE = re.compile(
    r"(?:que\s+(?:signifie|veut\s+dire|repr[ée]sente)|signification\s+de|"
    r"d[ée]veloppe(?:r|z)?\s+(?:l['’]acronyme|l['’]abr[ée]viation))",
    re.IGNORECASE,
)


def validate_exercise(exercise: PracticalExercise) -> list[str]:
    errors: list[str] = []
    if len(exercise.context.strip()) < MIN_CONTEXT_LENGTH:
        errors.append("Contexte insuffisant : décrire la situation (lieu, matériel, symptômes).")
    if not exercise.instructions or any(not i.strip() for i in exercise.instructions):
        errors.append("Consigne explicite requise.")
    if not exercise.criteria:
        errors.append("Barème requis.")
    if any(c.points <= 0 or not c.expected.strip() for c in exercise.criteria):
        errors.append("Chaque critère du barème doit avoir des points et un attendu.")
    if not exercise.justified_correction.strip():
        errors.append("Correction justifiée requise.")
    if not exercise.requirement_ids:
        errors.append("Au moins une exigence de la matrice doit être citée.")
    for req_id in exercise.requirement_ids:
        if req_id not in REQUIREMENTS_BY_ID:
            errors.append(f"Exigence inconnue : {req_id}.")
    texts = (exercise.title, exercise.context, *exercise.instructions)
    if any(_ACRONYM_EXPANSION_RE.search(t) for t in texts):
        errors.append("Question de développé d'acronyme interdite (ticket #192).")
    if re.search(r"\bofficiel", exercise.title, re.IGNORECASE):
        errors.append("Un exercice Jury Central n'est jamais présenté comme un sujet officiel.")
    return errors


def build_rubric(exercise: PracticalExercise) -> str:
    lines = [f"Barème sur {exercise.total_points:g} points :"]
    lines += [f"- {c.label} ({c.points:g} pt{"s" if c.points > 1 else ""}) : {c.expected}" for c in exercise.criteria]
    lines.append(f"Correction justifiée : {exercise.justified_correction}")
    return "\n".join(lines)


def build_prompt(exercise: PracticalExercise) -> str:
    numbered = "\n".join(f"{i}. {text}" for i, text in enumerate(exercise.instructions, start=1))
    return f"{exercise.context}\n\nConsignes :\n{numbered}"


def to_question_content(
    exercise: PracticalExercise, document_version_ids: list[int] | None = None
) -> dict:
    """Contenu prêt pour `app.v1.models.create_question` (type `exercise.question_type`),
    validé par le schéma du type existant. `document_version_ids` : versions des documents
    créés avec `create_source_document`, dans l'ordre de `exercise.documents`."""
    errors = validate_exercise(exercise)
    if errors:
        raise ValueError("; ".join(errors))
    ids = list(document_version_ids or [])
    if len(ids) != len(exercise.documents):
        raise ValueError("Une version de document source est requise par document de l'exercice.")
    content: dict = {
        "prompt": build_prompt(exercise),
        "rubric": build_rubric(exercise),
        "expected_points": [c.expected for c in exercise.criteria],
        "max_score": exercise.total_points,
    }
    if ids:
        content["source_document_version_id"] = ids[0]
        if len(ids) > 1:
            content["source_document_version_ids"] = ids
    spec = QUESTION_TYPE_REGISTRY.get(exercise.question_type)
    return spec.content_model.model_validate(content).model_dump(exclude_none=True)


# --- Exemple de format (non officiel, jamais importé dans la banque) ---------------------

# Données du schéma de l'exemple : côté prise murale conforme à T568B, côté PC avec les fils
# des broches 4 et 6 inversés (vert en 4, bleu en 6). Tableau et schéma en dérivent tous deux.
EXAMPLE_WALL_SIDE: tuple[str, ...] = T568B
EXAMPLE_PC_SIDE: tuple[str, ...] = T568B[:3] + (T568B[5], T568B[4], T568B[3]) + T568B[6:]

EXAMPLE_EXERCISE = PracticalExercise(
    code="EXEMPLE",
    title="Exemple de format — poste sans réseau après un déplacement de bureau",
    requirement_ids=("AP-34", "AP-37", "AP-C01"),
    context=(
        "Tu interviens dans une petite agence. Le poste de l'accueil a été déplacé dans le "
        "bureau voisin ; un collègue a refait sur place le câble entre la prise murale et le "
        "PC. Depuis, le PC n'a plus accès au réseau. La prise murale est câblée selon la norme "
        "T568B. Tu disposes d'un testeur de câble et d'une pince à sertir."
    ),
    documents=(
        ExerciseDocument(
            title="Document 1 — Relevé de l'intervention",
            kind="tableau",
            content_text=(
                "| Élément observé | Constat |\n"
                "|---|---|\n"
                "| Voyant du port réseau du PC | éteint |\n"
                "| Testeur de câble | fils 4 et 6 signalés croisés |\n"
                f"| Connecteur côté prise murale (broches 1 → 8) | {', '.join(EXAMPLE_WALL_SIDE)} |\n"
                f"| Connecteur côté PC (broches 1 → 8) | {', '.join(EXAMPLE_PC_SIDE)} |"
            ),
        ),
    ),
    instructions=(
        ("À partir du document 1, indique quel connecteur est mal réalisé et explique "
        "l'erreur."),
        "Donne l'ordre correct des couleurs, broche par broche, pour ce connecteur.",
        ("Décris, étape par étape, comment tu refais ce connecteur et comment tu vérifies "
        "ton travail."),
    ),
    criteria=(
        ScoringCriterion(
            label="Diagnostic",
            points=3,
            expected=(
                "Le connecteur côté PC est faux : les fils vert (broche 4) et bleu (broche 6) "
                "sont inversés par rapport à T568B, ce que confirme le testeur."
            ),
        ),
        ScoringCriterion(
            label="Code des couleurs",
            points=3,
            expected=(
                "T568B : blanc-orange, orange, blanc-vert, bleu, blanc-bleu, vert, "
                "blanc-marron, marron (même norme aux deux bouts : câble droit)."
            ),
        ),
        ScoringCriterion(
            label="Démarche de réalisation",
            points=3,
            expected=(
                "Couper l'ancien connecteur, dénuder la gaine, détorsader au minimum, ranger "
                "les fils dans l'ordre, couper droit, insérer jusqu'en butée, sertir."
            ),
        ),
        ScoringCriterion(
            label="Vérification",
            points=1,
            expected="Contrôler au testeur (1 à 8 dans l'ordre), puis le voyant et l'accès réseau.",
        ),
    ),
    justified_correction=(
        "Côté prise murale, l'ordre correspond à T568B. Côté PC, le collègue a rangé les paires "
        "côte à côte : le vert se retrouve en broche 4 et le bleu en broche 6. La paire verte "
        "n'est plus sur les broches 3 et 6, d'où le croisement 4/6 détecté et l'absence de "
        "liaison. On refait donc le connecteur côté PC en T568B ; les deux extrémités étant "
        "dans la même norme, on obtient un câble droit, adapté entre une prise murale et un PC."
    ),
)


EXAMPLE_FIGURES: tuple[Figure, ...] = (
    Figure(
        key="exemple-rj45-prise",
        title="Document 2a — Connecteur côté prise murale",
        alt=(
            "Fiche RJ45 côté prise murale, broches 1 à 8 : "
            + ", ".join(EXAMPLE_WALL_SIDE) + "."
        ),
        caption=(
            "Document 2a — Connecteur côté prise murale, tel que relevé. Fiche vue côté "
            "contacts, languette dessous : broche 1 à gauche. Fils rayés = fils blancs à bande."
        ),
        svg=connector_pins_svg(EXAMPLE_WALL_SIDE, label="Côté prise murale"),
    ),
    Figure(
        key="exemple-rj45-pc",
        title="Document 2b — Connecteur côté PC",
        alt="Fiche RJ45 côté PC, broches 1 à 8 : " + ", ".join(EXAMPLE_PC_SIDE) + ".",
        caption=(
            "Document 2b — Connecteur côté PC, tel que relevé. Même orientation que le "
            "document 2a."
        ),
        svg=connector_pins_svg(EXAMPLE_PC_SIDE, label="Côté PC"),
    ),
)

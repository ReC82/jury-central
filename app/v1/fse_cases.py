"""Nouveaux cas FSE pour l'entraînement et l'examen blanc (ticket #129).

Les banques historiques (`app.v1.fse_bank`) reprennent les exemples commentés des cours :
une session finissait par réinterroger l'élève sur le mail de Karim ou l'affiche de
sécurité routière déjà analysés dans le cours. Ce module ajoute, cours par cours, des CAS
NOUVEAUX — autres situations, documents, protagonistes, objectifs et distracteurs, sur les
mêmes notions — et fait passer ces cas avant les exemples du cours lors de la sélection.

Principes :
- **Ajout uniquement.** Un cas = un `SourceDocument` (texte exact + mise en page
  `content_json["layout"]`, voir `app.v1.document_layouts.resolve_layout`) et ses
  questions, créés une fois (idempotent : un cas déjà présent, reconnu au titre exact de
  son document dans le module, n'est jamais recréé ni modifié). Aucune question ni aucun
  document existant n'est modifié : les anciennes sessions gardent leurs versions.
- **Questions `MANUAL`.** Les importeurs historiques testent la présence de questions
  `IMPORTED` pour savoir si leur banque existe : les cas utilisent `MANUAL` pour ne jamais
  bloquer ni dupliquer cet import.
- **Visuel réellement présent.** Un cas qui s'appuie sur une illustration (affiche…)
  référence un `Asset` (fichier livré sous `app/static/`, empreinte SHA-256, prompt ou
  méthode de production, modèle) via `SourceDocumentVersion.asset_id`. Fichier absent →
  le cas n'est pas importé ; asset invalidé ou fichier disparu → ses questions ne sont
  plus servies (`unusable_document_question_ids`). Jamais une description à la place
  d'un visuel manquant, jamais d'appel de génération à l'affichage, à la reprise ou au
  seed.
- **Même texte pour l'élève et le correcteur.** Le texte exact du document
  (`content_text`) est celui transmis à la correction ; chaque texte affiché par la mise
  en page en est un extrait exact (vérifié par `tests/test_ticket129_fse_cases.py`) et la
  description de l'illustration correspond au dessin livré.
- **Priorité aux cas nouveaux** (`case_rank`) : 0 = cas nouveau jamais vu par l'élève (ou
  question sans document), 1 = cas nouveau dont l'élève a déjà vu le document (autre
  question du même cas, en entraînement ou en examen), 2 = exemple commenté du cours.
  Utilisé par `app.v1.session_service.compose_selection` après la difficulté demandée,
  jamais à sa place."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les types (#40) au chargement
from app.v1.assets import AssetError, AssetSpec, get_or_create_asset, static_path
from app.v1.models import (
    Asset,
    ContentStatus,
    GenerationSource,
    Question,
    QuestionDifficulty,
    QuestionVersion,
    SourceDocument,
    SourceDocumentVersion,
    UserQuestionHistory,
    create_question,
    create_source_document,
)
from app.v1.question_engine import validate_content

# Questions d'un cas : (type, contenu, difficulté). `{doc}` dans une valeur de
# `source_document_version_id` est remplacé par l'id réel de la version du document.
CaseQuestion = tuple[str, dict[str, Any], QuestionDifficulty]
DOC = "{doc}"


@dataclass(frozen=True)
class FseCase:
    """Un cas nouveau : un document (facultatif) et les questions qui s'y rapportent."""

    course_code: str
    key: str
    questions: tuple[CaseQuestion, ...]
    title: str | None = None
    content_text: str | None = None
    layout: dict[str, Any] | None = None
    illustration: AssetSpec | None = None


@dataclass(frozen=True)
class CourseExamples:
    """Exemples commentés d'un cours : titres exacts des documents repris par sa banque
    historique et noms propres qui signalent une question construite sur ces exemples
    sans document rattaché (ex. classement citant « le mail de Karim Haddad »)."""

    document_titles: frozenset[str]
    markers: tuple[str, ...] = field(default_factory=tuple)


def _registry() -> tuple[dict[str, tuple[FseCase, ...]], dict[str, CourseExamples]]:
    from app.v1.fse01_cases import FSE01_CASES, FSE01_EXAMPLES
    from app.v1.fse02_cases import FSE02_CASES, FSE02_EXAMPLES
    from app.v1.fse03_cases import FSE03_CASES, FSE03_EXAMPLES
    from app.v1.fse04_cases import FSE04_CASES, FSE04_EXAMPLES
    from app.v1.fse05_cases import FSE05_CASES, FSE05_EXAMPLES
    from app.v1.fse06_cases import FSE06_CASES, FSE06_EXAMPLES
    from app.v1.fse07_cases import FSE07_CASES, FSE07_EXAMPLES
    from app.v1.fse08_cases import FSE08_CASES, FSE08_EXAMPLES
    from app.v1.fse09_cases import FSE09_CASES, FSE09_EXAMPLES
    from app.v1.fse10_cases import FSE10_CASES, FSE10_EXAMPLES
    from app.v1.fse11_cases import FSE11_CASES, FSE11_EXAMPLES
    from app.v1.fse12_cases import FSE12_CASES, FSE12_EXAMPLES

    return (
        {
            "FSE01": FSE01_CASES, "FSE02": FSE02_CASES, "FSE03": FSE03_CASES, "FSE04": FSE04_CASES,
            "FSE05": FSE05_CASES, "FSE06": FSE06_CASES, "FSE07": FSE07_CASES, "FSE08": FSE08_CASES,
            "FSE09": FSE09_CASES, "FSE10": FSE10_CASES, "FSE11": FSE11_CASES, "FSE12": FSE12_CASES,
        },
        {
            "FSE01": FSE01_EXAMPLES, "FSE02": FSE02_EXAMPLES, "FSE03": FSE03_EXAMPLES,
            "FSE04": FSE04_EXAMPLES, "FSE05": FSE05_EXAMPLES, "FSE06": FSE06_EXAMPLES,
            "FSE07": FSE07_EXAMPLES, "FSE08": FSE08_EXAMPLES, "FSE09": FSE09_EXAMPLES,
            "FSE10": FSE10_EXAMPLES, "FSE11": FSE11_EXAMPLES, "FSE12": FSE12_EXAMPLES,
        },
    )


def cases_for(course_code: str) -> tuple[FseCase, ...]:
    return _registry()[0].get(course_code, ())


def all_cases() -> tuple[FseCase, ...]:
    return tuple(case for cases in _registry()[0].values() for case in cases)


def course_examples() -> dict[str, CourseExamples]:
    return _registry()[1]


# --- Import ------------------------------------------------------------------------------


def _existing_case_titles(db: Session, module_id: int) -> set[str]:
    rows = (
        db.query(SourceDocumentVersion.title)
        .join(SourceDocument, SourceDocument.id == SourceDocumentVersion.source_document_id)
        .filter(SourceDocument.module_id == module_id)
        .all()
    )
    return {row[0] for row in rows if row[0]}


def _existing_case_keys(db: Session, uaa_id: int) -> set[str]:
    """Cas sans document : reconnus à la clé `case_key` de leurs questions."""
    keys = set()
    for (content,) in (
        db.query(QuestionVersion.content_json)
        .join(Question, Question.current_version_id == QuestionVersion.id)
        .filter(Question.uaa_id == uaa_id, Question.generation_source == GenerationSource.MANUAL)
        .all()
    ):
        if isinstance(content, dict) and content.get("case_key"):
            keys.add(content["case_key"])
    return keys


def import_fse_cases(db: Session, module: Module, uaa: UAA) -> int:
    """Importe les cas nouveaux du cours `uaa` encore absents (voir docstring du module).
    Retourne le nombre de questions créées. Un cas dont l'illustration est absente sur
    disque est ignoré (rien de partiel) et sera importé dès que le fichier existera."""
    cases = cases_for(uaa.code)
    if not cases:
        return 0
    titles = _existing_case_titles(db, module.id)
    keys = _existing_case_keys(db, uaa.id)
    created = 0
    for case in cases:
        if (case.title and case.title in titles) or (not case.title and case.key in keys):
            continue
        asset_id = None
        if case.illustration is not None:
            try:
                asset_id = get_or_create_asset(db, case.illustration).id
            except AssetError:
                continue
        doc_version_id = None
        if case.title:
            content_json = {"layout": case.layout, "case_key": case.key} if case.layout else {"case_key": case.key}
            document = create_source_document(
                db, title=case.title, content_text=case.content_text, content_json=content_json,
                module_id=module.id, asset_id=asset_id,
            )
            db.flush()
            doc_version_id = document.current_version_id
        for question_type, content, difficulty in case.questions:
            content = {**content, "case_key": case.key}
            if content.get("source_document_version_id") == DOC:
                content["source_document_version_id"] = doc_version_id
            validate_content(question_type, 1, content)
            create_question(
                db, module_id=module.id, uaa_id=uaa.id, question_type=question_type,
                content_json=content, generation_source=GenerationSource.MANUAL,
                difficulty_declared=difficulty,
                source_document_version_id=content.get("source_document_version_id"),
            )
            created += 1
    db.flush()
    return created


# --- Visuels indisponibles ---------------------------------------------------------------


def unusable_document_question_ids(db: Session) -> set[int]:
    """Questions dont le document courant dépend d'une illustration inutilisable (asset
    non ACTIVE ou fichier absent du disque) : jamais servies dans une nouvelle session —
    une question ne s'appuie jamais sur la description d'un visuel absent. Les sessions
    déjà créées ne sont pas modifiées."""
    rows = (
        db.query(Question.id, Asset)
        .join(QuestionVersion, QuestionVersion.id == Question.current_version_id)
        .join(SourceDocumentVersion, SourceDocumentVersion.id == QuestionVersion.source_document_version_id)
        .join(Asset, Asset.id == SourceDocumentVersion.asset_id)
        .all()
    )
    unusable: set[int] = set()
    usable_cache: dict[int, bool] = {}
    for question_id, asset in rows:
        if asset.id not in usable_cache:
            usable_cache[asset.id] = asset.status == ContentStatus.ACTIVE and bool(
                asset.storage_ref and static_path(asset.storage_ref).is_file()
            )
        if not usable_cache[asset.id]:
            unusable.add(question_id)
    return unusable


# --- Priorité aux cas nouveaux -----------------------------------------------------------

FRESH, SEEN_CASE, COURSE_EXAMPLE = 0, 1, 2


def _full_text(content: dict) -> str:
    parts: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, str):
            parts.append(node)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(content)
    return " ".join(parts)


def is_course_example(question: Question) -> bool:
    """Question construite sur un exemple commenté de son cours (document repris du cours
    ou nom propre de cet exemple dans l'énoncé)."""
    uaa = question.uaa
    examples = course_examples().get(uaa.code) if uaa is not None else None
    version = question.current_version
    if examples is None or version is None:
        return False
    document = version.source_document_version
    if document is not None and document.title in examples.document_titles:
        return True
    text = _full_text(version.content_json or {})
    return any(marker in text for marker in examples.markers)


def _seen_document_ids(db: Session, user_id: int) -> set[int]:
    rows = (
        db.query(SourceDocumentVersion.source_document_id)
        .join(QuestionVersion, QuestionVersion.source_document_version_id == SourceDocumentVersion.id)
        .join(Question, Question.current_version_id == QuestionVersion.id)
        .join(UserQuestionHistory, UserQuestionHistory.question_id == Question.id)
        .filter(UserQuestionHistory.user_id == user_id)
        .distinct()
        .all()
    )
    return {row[0] for row in rows}


def case_ranker(db: Session, *, user_id: int) -> Callable[[Question], int]:
    """Rang de priorité d'une question pour cet élève (voir docstring du module). Toute
    question hors des cours qui déclarent des exemples (Informatique, Français…) vaut 0 :
    leur sélection reste strictement inchangée."""
    examples = course_examples()
    seen_documents: set[int] | None = None

    def rank(question: Question) -> int:
        nonlocal seen_documents
        uaa = question.uaa
        if uaa is None or uaa.code not in examples:
            return FRESH
        if is_course_example(question):
            return COURSE_EXAMPLE
        version = question.current_version
        document = version.source_document_version if version is not None else None
        if document is None:
            return FRESH
        if seen_documents is None:
            seen_documents = _seen_document_ids(db, user_id)
        return SEEN_CASE if document.source_document_id in seen_documents else FRESH

    return rank

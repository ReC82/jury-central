"""Banque des cours du parcours « AMPCR — Pratique écrite » (ticket #193, premier cours PR06).

Branchement sur le moteur de sessions existant, sans nouveau système :
- un cours pratique est une UAA du module `AMPCR-PRATIQUE` (slug `ampcr-pratique-pr06`) ;
- `PRACTICAL_COURSES` liste les cours réellement rédigés (jamais un emplacement vide) et
  leur contexte pédagogique de correction (`PedagogicalContext`) ;
- les questions sont importées à la demande (`import_practical_bank`, idempotent), avec
  leurs documents structurés (tableaux) ;
- **réserves séparées** : `QuestionVersion.prompt_version` vaut
  `ampcr-pratique-<code>:practice` (exercices du cours, « S'entraîner ») ou
  `…:exam` (mini-examen, « Examen blanc ») ; `restrict_to_mode` filtre la sélection de la
  banque selon le mode de la session. Les questions des autres matières ne portent pas ce
  préfixe et ne sont jamais filtrées ;
- **pas de génération IA** pour ces cours (`is_practical_code`) : l'épreuve pratique exige
  des questions vérifiées, contextualisées et barémées ; la correction reste celle du moteur
  (IA batch avec le barème, correction locale pour la classification).
"""

from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.schemas import PedagogicalContext
from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les types (#40) au chargement
from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import PRACTICAL_MODULE_CODE
from app.v1.ampcr_pratique_pr06_bank import ALL_ITEMS as PR06_ITEMS
from app.v1.ampcr_pratique_pr06_bank import PR06Item
from app.v1.models import (
    GenerationSource,
    Question,
    QuestionVersion,
    create_question,
    create_source_document,
)
from app.v1.question_engine import validate_content

PROMPT_VERSION_PREFIX = "ampcr-pratique"
SHORT_ANSWER_MAX_LENGTH = 3000
LONG_ANSWER_MAX_LENGTH = 20000


@dataclass(frozen=True)
class PracticalCourse:
    code: str
    title: str
    items: tuple[PR06Item, ...]
    context: PedagogicalContext

    @property
    def slug(self) -> str:
        return f"ampcr-pratique-{self.code.lower()}"


_PR06_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr06",
    course_title="AMPCR pratique écrite — PR06 Diagnostic des pannes matérielles",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien, sans matériel réel"
    ),
    allowed_notions=[
        "recueil des symptômes, chronologie, changements récents, données et autorisations",
        "observation, hypothèse, test, résultat, conclusion ; du plus simple au plus invasif",
        "reproduction sans aggraver, un changement à la fois, configuration minimale, test croisé avec un composant connu fonctionnel",
        "sécurité : coupure secteur, décharge résiduelle, ESD, ne jamais ouvrir un bloc d'alimentation ni une batterie gonflée",
        "chaîne de démarrage : secteur, bloc d'alimentation, carte mère, POST, firmware BIOS/UEFI, stockage, chargeur, système",
        "PC inerte, ventilateurs sans image, absence de POST, « No boot device », redémarrages, écrans bleus, extinctions sous charge",
        "bips, LED et codes POST propres à chaque fabricant (manuel)",
        "RAM (barrette, slot, compatibilité, test mémoire, ECC), processeur et refroidissement (température, throttling, arrêt de protection)",
        "bloc d'alimentation (puissance, connecteurs ATX 24, EPS, PCIe, SATA, testeur), carte mère (condensateurs, VRM, liquide)",
        "affichage (écran, entrée, câble, sortie de la carte graphique ou iGPU), stockage (HDD, SSD, SATA, M.2 SATA/NVMe, SMART comme indice), périphériques et pilotes",
        "compatibilité : socket, génération DDR, format, alimentation, PCIe, SATA/M.2, firmware ; documentation du fabricant",
        "journaux (Kernel-Power 41, codes d'arrêt), indices et preuves, escalade, priorité aux données, compte rendu",
    ],
    competencies=[
        "Rédiger une démarche de diagnostic ordonnée et justifiée à partir d'un cas écrit",
        "Interpréter un document technique fictif (relevé, journal, manuel, rapport SMART, températures)",
        "Proposer une intervention sûre, sa vérification et un compte rendu professionnel",
    ],
    vocabulary=[
        "POST", "firmware", "UEFI", "CSM", "PWR_OK", "+5 VSB", "EPS", "configuration minimale",
        "test croisé", "SMART", "throttling", "Kernel-Power 41", "ESD",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation "
        "techniquement juste, sans exiger de mot-clé ; suivre le barème de la question ; "
        "pénaliser une action dangereuse (sous tension, ouverture d'un bloc d'alimentation ou "
        "d'une batterie) ou destructive pour les données sans sauvegarde ni accord ; ne jamais "
        "valider une correspondance universelle de bips ou de codes POST."
    ),
)

PRACTICAL_COURSES: tuple[PracticalCourse, ...] = (
    PracticalCourse(
        code="PR06", title="Diagnostic des pannes matérielles", items=PR06_ITEMS, context=_PR06_CONTEXT
    ),
)
PRACTICAL_COURSES_BY_CODE: dict[str, PracticalCourse] = {c.code: c for c in PRACTICAL_COURSES}
PRACTICAL_COURSES_BY_SLUG: dict[str, PracticalCourse] = {c.slug: c for c in PRACTICAL_COURSES}


def get_practical_course_by_slug(uaa_slug: str) -> PracticalCourse | None:
    return PRACTICAL_COURSES_BY_SLUG.get(uaa_slug)


def is_practical_code(uaa_code: str | None) -> bool:
    return bool(uaa_code) and uaa_code in PRACTICAL_COURSES_BY_CODE


def get_practical_context(uaa_code: str | None) -> PedagogicalContext | None:
    course = PRACTICAL_COURSES_BY_CODE.get(uaa_code or "")
    return course.context if course else None


def usage_tag(code: str, usage: str) -> str:
    return f"{PROMPT_VERSION_PREFIX}-{code.lower()}:{usage}"


def restrict_to_mode(questions: list[Question], mode_value: str | None) -> list[Question]:
    """Garde, pour les questions du parcours pratique, celles de la réserve du mode
    (`practice`/`exam`). No-op pour toute autre question et quand `mode_value` est absent."""
    if mode_value is None:
        return questions
    return [q for q in questions if question_usage(q) in (None, mode_value)]


def _document_layout(document: ExerciseDocument) -> dict | None:
    if document.kind != "tableau":
        return None
    rows = document.table_rows()
    return {"kind": "table", "columns": rows[0], "rows": rows[1:]}


def _create_documents(db: Session, module: Module, item: PR06Item) -> list[int]:
    ids = []
    for document in item.documents:
        layout = _document_layout(document)
        created = create_source_document(
            db,
            title=document.title,
            content_text=document.content_text,
            content_json={"layout": layout} if layout else None,
            module_id=module.id,
        )
        ids.append(created.current_version_id)
    db.flush()
    return ids


def item_content(item: PR06Item, document_version_ids: list[int]) -> dict:
    """Contenu `content_json` d'une question, au format d'un type existant."""
    content: dict = {"prompt": item.prompt}
    if item.question_type == "classification":
        assert item.classification is not None
        content.update(
            categories=list(item.classification.categories),
            elements=list(item.classification.elements),
            correct_categories=list(item.classification.correct),
            explanation=" ".join(item.correction),
        )
    else:
        content["rubric"] = item.rubric()
        if item.question_type == "short_answer":
            content["max_length"] = SHORT_ANSWER_MAX_LENGTH
        else:
            content.update(
                expected_points=[c.expected for c in item.criteria],
                max_score=item.total_points,
                max_length=LONG_ANSWER_MAX_LENGTH,
            )
    if document_version_ids:
        content["source_document_version_id"] = document_version_ids[0]
        if len(document_version_ids) > 1:
            content["source_document_version_ids"] = list(document_version_ids)
    return content


def import_practical_bank(db: Session, module: Module, uaa: UAA) -> int:
    """Importe la banque d'un cours pratique (idempotent : rien si l'UAA a déjà ses
    questions importées)."""
    course = PRACTICAL_COURSES_BY_CODE.get(uaa.code)
    if course is None or module.code != PRACTICAL_MODULE_CODE:
        return 0
    already = (
        db.query(Question)
        .filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED)
        .count()
    )
    if already:
        return 0
    imported = 0
    for item in course.items:
        document_ids = _create_documents(db, module, item)
        content = item_content(item, document_ids)
        validate_content(item.question_type, 1, content)
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=item.question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            prompt_version=usage_tag(course.code, item.usage),
            source_program_version="Consignes AMPCR pratique 2026-2027/1",
            source_document_version_id=document_ids[0] if document_ids else None,
        )
        imported += 1
    db.flush()
    return imported


PRACTICAL_BANK_IMPORTERS: dict[str, Callable[[Session, Module, UAA], int]] = {
    course.slug: import_practical_bank for course in PRACTICAL_COURSES
}


def _version_usage(version: QuestionVersion | None) -> str | None:
    tag = (version.prompt_version if version else None) or ""
    if not tag.startswith(PROMPT_VERSION_PREFIX) or ":" not in tag:
        return None
    return tag.rsplit(":", 1)[1]


def question_usage(question: Question) -> str | None:
    """Réserve (`practice`/`exam`) d'une question du parcours pratique, `None` sinon. Lue
    sur la version courante, sinon sur la première version marquée : une nouvelle version
    créée plus tard (correction, administration) ne change jamais de réserve."""
    usage = _version_usage(question.current_version)
    if usage is None:
        for version in sorted(question.versions, key=lambda v: v.version):
            usage = _version_usage(version)
            if usage is not None:
                break
    return usage

"""Références documentaires résolvables (ticket #151).

Une question extraite d'un dossier (FSE02, FSE04, FSE07, FSE16…), servie seule en
entraînement, en examen blanc FSE17 ou en quiz, ne doit jamais renvoyer à un document que
l'élève ne voit pas : « D'après le document 3 » doit montrer un document réellement
numéroté 3, et « Le forum affirme… La note de direction mentionne… » doit montrer le forum
ET la note. Les documents affichés sont ceux du payload public
(`source_document_version_id` / `source_document_version_ids`), exactement ceux que reçoit
le correcteur (`app.v1.session_service._referenced_document_ids`, ticket #77).

`DOSSIER_REPAIRS` est la seule liste des questions corrigées : la banque
(`app.v1.fse_bank`) crée directement le contenu corrigé, et
`repair_dossier_references` met à niveau une banque déjà importée par une NOUVELLE
`QuestionVersion` (jamais une version modifiée en place : les sessions déjà générées
gardent la version qu'elles ont servie, pour la reprise, la correction et l'export).

`audit_document_references` relit toutes les questions actives et liste les renvois
non résolus (numéro absent, document nommé absent, « les deux/trois documents »
incomplet, renvoi sans aucun document)."""

import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import UAA
from app.v1 import question_types  # noqa: F401 — enregistre les types (seed hors banque)
from app.v1.models import (
    ContentStatus,
    Question,
    QuestionVersion,
    SourceDocumentVersion,
    add_question_version,
)
from app.v1.question_engine import public_payload, validate_content

# Consignes reformulées : le renvoi numéroté nomme aussi le document visé, tel qu'il est
# affiché (« Document 3 — Réactions des groupes concernés »), sans changer la question.
# Remise en ordre (type sans document) : les trois documents sont décrits dans les
# éléments à classer ; la consigne le dit au lieu de renvoyer à « ces trois documents ».
FSE07_RELIABILITY_ORDER_PROMPT = (
    "Classe les trois documents du dossier, décrits ci-dessous, du plus fiable au moins "
    "fiable, selon les critères auteur/date/contexte/preuves."
)
FSE16_ASSOCIATION_LIMIT_PROMPT = (
    "D'après le document 3 (réactions des groupes concernés), quelle limite l'association "
    "environnementale met-elle en évidence concernant l'effet de réduction de la voiture "
    "individuelle ?"
)
FSE16_TRANSPORT_COMPANY_PROMPT = (
    "Analyse la réaction de l'entreprise de transport (document 3, réactions des groupes "
    "concernés) : quel effet attendu et quelle limite/coût y identifies-tu ?"
)
FSE16_CONCLUSION_PROMPT = (
    "Rédige une conclusion argumentée sur la proposition d'aide aux transports, fondée sur "
    "les trois documents fournis (documents 1, 2 et 3)."
)


@dataclass(frozen=True)
class DossierRepair:
    uaa_code: str
    old_prompt: str
    new_prompt: str
    # Titres exacts des documents à montrer, dans l'ordre du dossier.
    document_titles: tuple[str, ...]


def _titles():
    from app.v1.fse02_content import FSE02_FREE_AD_TITLE, FSE02_PAID_TITLE, FSE02_PUBLIC_TITLE
    from app.v1.fse04_content import FSE04_GROUP_TITLE, FSE04_TESTIMONY_TITLE
    from app.v1.fse07_content import FSE07_CHAT_TITLE, FSE07_FORUM_TITLE, FSE07_SCHOOL_TITLE
    from app.v1.fse16_content import (
        FSE16_BUDGET_NOTE_TITLE,
        FSE16_PROPOSAL_TITLE,
        FSE16_REACTIONS_TITLE,
    )

    return {
        "fse02": (FSE02_PAID_TITLE, FSE02_FREE_AD_TITLE, FSE02_PUBLIC_TITLE),
        "fse04": (FSE04_GROUP_TITLE, FSE04_TESTIMONY_TITLE),
        "fse07": (FSE07_SCHOOL_TITLE, FSE07_CHAT_TITLE, FSE07_FORUM_TITLE),
        "fse16": (FSE16_PROPOSAL_TITLE, FSE16_BUDGET_NOTE_TITLE, FSE16_REACTIONS_TITLE),
    }


def dossier_repairs() -> tuple[DossierRepair, ...]:
    t = _titles()
    paid, free_ad, public = t["fse02"]
    group, testimony = t["fse04"]
    school, chat, forum = t["fse07"]
    proposal, budget_note, reactions = t["fse16"]
    return (
        DossierRepair(
            "FSE02",
            "Classe chacun de ces trois médias selon son mode de financement principal.",
            "Classe chacun de ces trois médias selon son mode de financement principal.",
            (paid, free_ad, public),
        ),
        DossierRepair(
            "FSE02",
            "Compare L'Hebdo du Littoral et Le Flash Infos : lequel des deux dépend le plus de "
            "son audience pour obtenir des revenus ? Justifie ta réponse.",
            "Compare L'Hebdo du Littoral et Le Flash Infos : lequel des deux dépend le plus de "
            "son audience pour obtenir des revenus ? Justifie ta réponse.",
            (paid, free_ad),
        ),
        DossierRepair(
            "FSE04",
            "Explique pourquoi on ne peut pas dire que « le groupe a obligé tout le monde à se "
            "moquer », en t'appuyant sur les deux documents.",
            "Explique pourquoi on ne peut pas dire que « le groupe a obligé tout le monde à se "
            "moquer », en t'appuyant sur les deux documents.",
            (group, testimony),
        ),
        DossierRepair(
            "FSE07",
            "Classe ces trois documents du plus fiable au moins fiable, selon les critères "
            "auteur/date/contexte/preuves.",
            FSE07_RELIABILITY_ORDER_PROMPT,
            (),
        ),
        DossierRepair(
            "FSE07",
            "Pourquoi le document du forum est-il moins fiable que la note de direction ? Cite un indice précis.",
            "Pourquoi le document du forum est-il moins fiable que la note de direction ? Cite un indice précis.",
            (school, forum),
        ),
        DossierRepair(
            "FSE07",
            "Le forum affirme que Lucas a été « humilié devant toute l'école ». La note de "
            "direction mentionne un groupe de 24 élèves. Quel fait retiens-tu, et pourquoi ?",
            "Le forum affirme que Lucas a été « humilié devant toute l'école ». La note de "
            "direction mentionne un groupe de 24 élèves. Quel fait retiens-tu, et pourquoi ?",
            (school, forum),
        ),
        DossierRepair(
            "FSE07",
            "Le forum affirme que « la direction n'a strictement rien fait ». Sachant que la "
            "note de direction précise que « la vidéo a été supprimée du groupe à la demande "
            "de la direction », évalue la fiabilité de cette affirmation du forum et explique "
            "ta démarche.",
            "Le forum affirme que « la direction n'a strictement rien fait ». Sachant que la "
            "note de direction précise que « la vidéo a été supprimée du groupe à la demande "
            "de la direction », évalue la fiabilité de cette affirmation du forum et explique "
            "ta démarche.",
            (school, forum),
        ),
        DossierRepair(
            "FSE07",
            "Rédige une conclusion argumentée pour ce dossier : identifie un enjeu juridique et "
            "un enjeu sociologique, en citant au moins un élément précis d'un document fiable "
            "pour chacun.",
            "Rédige une conclusion argumentée pour ce dossier : identifie un enjeu juridique et "
            "un enjeu sociologique, en citant au moins un élément précis d'un document fiable "
            "pour chacun.",
            (school, chat, forum),
        ),
        # Ticket #152 : le document 3 commence par « Cette aide… » ; la proposition
        # (document 1) l'accompagne pour que l'aide soit décrite.
        DossierRepair(
            "FSE16",
            "D'après le document 3, quelle limite l'association environnementale met-elle en "
            "évidence concernant l'effet de réduction de la voiture individuelle ?",
            FSE16_ASSOCIATION_LIMIT_PROMPT,
            (proposal, reactions),
        ),
        DossierRepair(
            "FSE16",
            "Analyse la réaction de l'entreprise de transport (document 3) : quel effet attendu "
            "et quelle limite/coût y identifies-tu ?",
            FSE16_TRANSPORT_COMPANY_PROMPT,
            (proposal, reactions),
        ),
        DossierRepair(
            "FSE16",
            "Rédige une conclusion argumentée sur la proposition d'aide aux transports, fondée "
            "sur les trois documents fournis.",
            FSE16_CONCLUSION_PROMPT,
            (proposal, budget_note, reactions),
        ),
    )


def _uaa_documents(db: Session, uaa: UAA) -> dict[str, int]:
    """Titre → version courante des documents du dossier de cette UAA (ceux que ses
    questions référencent déjà) — jamais un document homonyme d'un autre cours."""
    versions = (
        db.query(QuestionVersion)
        .join(Question, Question.current_version_id == QuestionVersion.id)
        .filter(Question.uaa_id == uaa.id)
        .all()
    )
    ids: set[int] = set()
    for version in versions:
        content = version.content_json or {}
        if content.get("source_document_version_id"):
            ids.add(content["source_document_version_id"])
        ids.update(content.get("source_document_version_ids") or [])
    if not ids:
        return {}
    return {doc.title: doc.id for doc in db.query(SourceDocumentVersion).filter(SourceDocumentVersion.id.in_(ids))}


def repair_dossier_references(db: Session) -> dict[str, int]:
    """Met à niveau une banque déjà importée (idempotent) : nouvelle version pour chaque
    question de `dossier_repairs()` dont la version courante a encore l'ancienne consigne
    ou ne montre pas tous les documents nécessaires. Les anciennes versions et les
    sessions qui les ont servies restent intactes."""
    repaired = 0
    unresolved = 0
    by_uaa: dict[str, list[DossierRepair]] = {}
    for repair in dossier_repairs():
        by_uaa.setdefault(repair.uaa_code, []).append(repair)
    for uaa_code, repairs in by_uaa.items():
        uaa = db.query(UAA).filter_by(code=uaa_code).first()
        if uaa is None:
            continue
        documents = _uaa_documents(db, uaa)
        questions = (
            db.query(Question)
            .filter(Question.uaa_id == uaa.id, Question.status == ContentStatus.ACTIVE)
            .all()
        )
        for repair in repairs:
            wanted_ids = [documents.get(title) for title in repair.document_titles]
            for question in questions:
                version = question.current_version
                content = dict((version.content_json if version else None) or {})
                if content.get("prompt") not in (repair.old_prompt, repair.new_prompt):
                    continue
                if None in wanted_ids:
                    unresolved += 1
                    continue
                if not wanted_ids:
                    # Consigne seule (type sans document, éléments déjà décrits).
                    if content.get("prompt") == repair.new_prompt:
                        continue
                    content["prompt"] = repair.new_prompt
                    validate_content(version.question_type, version.schema_version, content)
                    add_question_version(
                        db,
                        question,
                        question_type=version.question_type,
                        content_json=content,
                        generator_model=version.generator_model,
                        prompt_version=version.prompt_version,
                        source_program_version=version.source_program_version,
                        source_document_version_id=version.source_document_version_id,
                    )
                    repaired += 1
                    continue
                target_ids = wanted_ids if len(wanted_ids) > 1 else None
                primary = content.get("source_document_version_id")
                if primary not in wanted_ids:
                    primary = wanted_ids[0]
                if (
                    content.get("prompt") == repair.new_prompt
                    and content.get("source_document_version_ids") == target_ids
                    and content.get("source_document_version_id") == primary
                ):
                    continue
                content["prompt"] = repair.new_prompt
                content["source_document_version_id"] = primary
                if target_ids:
                    content["source_document_version_ids"] = target_ids
                else:
                    content.pop("source_document_version_ids", None)
                validate_content(version.question_type, version.schema_version, content)
                add_question_version(
                    db,
                    question,
                    question_type=version.question_type,
                    content_json=content,
                    generator_model=version.generator_model,
                    prompt_version=version.prompt_version,
                    source_program_version=version.source_program_version,
                    source_document_version_id=content.get("source_document_version_id"),
                )
                repaired += 1
    db.flush()
    return {"repaired": repaired, "unresolved": unresolved}


# =========================================================================================
# Audit
# =========================================================================================

_NUMBERED = re.compile(r"\bdocument\s+(\d+)\b", re.IGNORECASE)
_COUNTED = re.compile(r"\b(?:les|ces)\s+(deux|trois|quatre)\s+documents\b", re.IGNORECASE)
_COUNTS = {"deux": 2, "trois": 3, "quatre": 4}
# Renvois à « un » document sans numéro : il faut au moins un document affiché.
_GENERIC = re.compile(
    r"\b(d'après|selon) (le|la|les) (texte|document|tableau|schéma|note|publication|témoignage)|"
    r"\bdocuments? fournis\b|\bces (deux|trois|quatre) documents\b",
    re.IGNORECASE,
)
# Documents nommés par leur nature dans les consignes de dossier : le mot doit figurer
# dans le titre d'un document affiché (le forum peut aussi être cité DANS un document,
# ex. le commentaire de Sophie sur un forum de jeux vidéo, FSE03).
_NAMED = {
    "la note de direction": ("direction", False),
    "le forum": ("forum", True),
    "la note budgétaire": ("budgétaire", False),
}


def _without_quotes(prompt: str) -> str:
    """Une consigne citée entre guillemets (« Compare les deux documents fournis… ») est
    un objet d'étude, pas un renvoi de la question elle-même."""
    return re.sub(r"«[^»]*»", "«»", prompt)


def _shown_documents(db: Session, version: QuestionVersion) -> list[SourceDocumentVersion]:
    from app.v1.session_service import _referenced_document_ids, resolve_documents_in_order

    payload = public_payload(version.question_type, version.schema_version, version.content_json)
    return resolve_documents_in_order(db, _referenced_document_ids(payload))


def reference_problems(db: Session, version: QuestionVersion) -> list[str]:
    """Renvois de la consigne qu'aucun document affiché ne résout (vide = résolvable)."""
    from app.v1.document_layouts import display_heading, resolve_layout

    prompt = _without_quotes(str((version.content_json or {}).get("prompt", "")))
    documents = _shown_documents(db, version)
    problems: list[str] = []
    labels = {display_heading(doc, resolve_layout(doc), "")["label"].lower() for doc in documents}
    for number in sorted(set(_NUMBERED.findall(prompt))):
        if f"document {number}" not in labels:
            problems.append(f"« document {number} » non affiché")
    for word in _COUNTED.findall(prompt):
        if len(documents) < _COUNTS[word.lower()] and "décrits ci-dessous" not in prompt:
            problems.append(f"« {word} documents » mais {len(documents)} affiché(s)")
    for phrase, (keyword, in_text) in _NAMED.items():
        haystacks = [f"{doc.title} {doc.content_text if in_text else ''}".lower() for doc in documents]
        if phrase in prompt.lower() and not any(keyword in haystack for haystack in haystacks):
            problems.append(f"« {phrase} » non affichée")
    if not documents and _GENERIC.search(prompt) and "décrits ci-dessous" not in prompt:
        problems.append("renvoi à un document sans document affiché")
    return problems


def audit_document_references(db: Session, *, uaa_codes: tuple[str, ...] | None = None) -> dict:
    """Audit de toutes les questions actives (ou de certaines UAA) : nombre de questions
    relues, de questions comportant un renvoi documentaire, et renvois non résolus."""
    query = (
        db.query(Question, UAA.code)
        .outerjoin(UAA, UAA.id == Question.uaa_id)
        .filter(Question.status == ContentStatus.ACTIVE)
    )
    if uaa_codes:
        query = query.filter(UAA.code.in_(uaa_codes))
    audited = 0
    with_reference = 0
    unresolved: list[dict] = []
    for question, code in query.all():
        version = question.current_version
        if version is None:
            continue
        audited += 1
        prompt = _without_quotes(str((version.content_json or {}).get("prompt", "")))
        if (
            _NUMBERED.search(prompt)
            or _COUNTED.search(prompt)
            or _GENERIC.search(prompt)
            or any(phrase in prompt.lower() for phrase in _NAMED)
        ):
            with_reference += 1
        problems = reference_problems(db, version)
        if problems:
            unresolved.append({"question_id": question.id, "uaa": code, "prompt": prompt, "problems": problems})
    return {"audited": audited, "with_reference": with_reference, "unresolved": unresolved}

"""Migration ponctuelle (finalisation Informatique) : un staging déjà seedé avant cette
session garde le contenu MC04/MC08 pré-correctif (SMART non développé, `> 2 To` cassé)
puisque `seed()` ne modifie jamais un bloc déjà présent par titre. Ce test vérifie que
`_refresh_stale_ampcr_course_content` corrige ces deux blocs précis SANS toucher un
contenu différent (ex. légitimement modifié depuis l'admin)."""

from app.models import UAA, LessonBlock, Module, Subject
from app.seed import (
    _MC04_STALE_CONTENT,
    _MC08_STALE_CONTENT,
    _refresh_stale_ampcr_course_content,
)
from app.v1.ampcr_courses import AMPCR_COURSE_MARKDOWN

# Reconstitue un texte de bloc "pré-correctif" minimal mais réaliste : le marqueur exact
# recherché par `_refresh_stale_ampcr_course_content`, entouré d'un peu de contexte —
# suffisant pour exercer le mécanisme sans dépendre d'un fichier externe non versionné.
_STALE_MC04_BLOCK = f"# Stockage (avant correctif)\n\n## 2. Définitions essentielles\n{_MC04_STALE_CONTENT}\n"
_STALE_MC08_BLOCK = f"# Partitionnement (avant correctif)\n\n## 4. Procédure\nAvant de partitionner : {_MC08_STALE_CONTENT}\n"


def _make_ampcr_uaa(db_session, code: str, content: str) -> UAA:
    subject = db_session.query(Subject).filter_by(slug="informatique-refresh-test").first()
    if subject is None:
        subject = Subject(name="Informatique refresh test", slug="informatique-refresh-test")
        db_session.add(subject)
        db_session.flush()
    module = db_session.query(Module).filter_by(slug="ampcr-refresh-test").first()
    if module is None:
        module = Module(subject_id=subject.id, code="AMPCR", slug="ampcr-refresh-test")
        db_session.add(module)
        db_session.flush()
    uaa = UAA(code=code, title="t", slug=f"{code.lower()}-refresh-test", position=1, is_published=True, module_id=module.id)
    db_session.add(uaa)
    db_session.flush()
    db_session.add(LessonBlock(uaa=uaa, title="Cours de révision express", type="markdown", content=content, position=1))
    db_session.commit()
    return uaa


def test_refreshes_stale_mc04_and_mc08_blocks(db_session):
    _make_ampcr_uaa(db_session, "MC04", _STALE_MC04_BLOCK)
    _make_ampcr_uaa(db_session, "MC08", _STALE_MC08_BLOCK)

    refreshed = {"blocks": 0}
    _refresh_stale_ampcr_course_content(db_session, refreshed)
    db_session.commit()

    assert refreshed["blocks"] == 2

    mc04_block = (
        db_session.query(LessonBlock)
        .join(UAA, LessonBlock.uaa_id == UAA.id)
        .filter(UAA.code == "MC04", LessonBlock.title == "Cours de révision express")
        .first()
    )
    assert mc04_block.content == AMPCR_COURSE_MARKDOWN["MC04"]
    assert "Self-Monitoring, Analysis and Reporting Technology" in mc04_block.content

    mc08_block = (
        db_session.query(LessonBlock)
        .join(UAA, LessonBlock.uaa_id == UAA.id)
        .filter(UAA.code == "MC08", LessonBlock.title == "Cours de révision express")
        .first()
    )
    assert mc08_block.content == AMPCR_COURSE_MARKDOWN["MC08"]
    assert "\n> 2 To" not in mc08_block.content


def test_never_touches_content_that_differs_from_the_known_stale_text(db_session):
    """Un contenu légitimement édité depuis l'admin (donc différent du texte connu
    d'avant correctif) ne doit JAMAIS être écrasé."""
    edited_content = "Contenu MC04 personnalisé par un formateur, différent du cours par défaut."
    _make_ampcr_uaa(db_session, "MC04", edited_content)

    refreshed = {"blocks": 0}
    _refresh_stale_ampcr_course_content(db_session, refreshed)
    db_session.commit()

    assert refreshed["blocks"] == 0
    block = (
        db_session.query(LessonBlock)
        .join(UAA, LessonBlock.uaa_id == UAA.id)
        .filter(UAA.code == "MC04", LessonBlock.title == "Cours de révision express")
        .first()
    )
    assert block.content == edited_content


def test_already_fresh_content_is_left_untouched(db_session):
    _make_ampcr_uaa(db_session, "MC04", AMPCR_COURSE_MARKDOWN["MC04"])

    refreshed = {"blocks": 0}
    _refresh_stale_ampcr_course_content(db_session, refreshed)
    db_session.commit()

    assert refreshed["blocks"] == 0


def test_is_idempotent(db_session):
    _make_ampcr_uaa(db_session, "MC04", _STALE_MC04_BLOCK)

    first = {"blocks": 0}
    _refresh_stale_ampcr_course_content(db_session, first)
    db_session.commit()
    second = {"blocks": 0}
    _refresh_stale_ampcr_course_content(db_session, second)
    db_session.commit()

    assert first["blocks"] == 1
    assert second["blocks"] == 0


def test_stale_markers_no_longer_present_in_fixed_source():
    assert _MC04_STALE_CONTENT not in AMPCR_COURSE_MARKDOWN["MC04"]
    assert _MC08_STALE_CONTENT not in AMPCR_COURSE_MARKDOWN["MC08"]

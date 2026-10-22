"""Ticket #83 — le développé SMART du cours MC04 doit atteindre une base déjà seedée.

`seed()` ne modifie jamais un bloc existant : `repair_mc04_smart_expansion` remplace
uniquement les fragments exacts d'avant correctif (voir `app.seed.MC04_SMART_FRAGMENTS`).
"""

from app.models import UAA, LessonBlock, Module, Subject
from app.seed import MC04_SMART_FRAGMENTS, repair_mc04_smart_expansion
from app.v1.ampcr_courses import AMPCR_COURSE_MARKDOWN

SMART_EXPANSION = "Self-Monitoring, Analysis and Reporting Technology"


def _stale_course() -> str:
    content = AMPCR_COURSE_MARKDOWN["MC04"]
    for stale, fixed in MC04_SMART_FRAGMENTS:
        content = content.replace(fixed, stale)
    return content


def _make_block(db_session, code: str, content: str) -> LessonBlock:
    subject = Subject(name=f"Info test {code}", slug=f"info-test-{code.lower()}")
    db_session.add(subject)
    db_session.flush()
    module = Module(subject_id=subject.id, code="AMPCR", slug=f"ampcr-test-{code.lower()}")
    db_session.add(module)
    db_session.flush()
    uaa = UAA(code=code, title="t", slug=f"{code.lower()}-test", position=1,
              is_published=True, module_id=module.id)
    db_session.add(uaa)
    db_session.flush()
    block = LessonBlock(uaa=uaa, title="Cours de révision express", type="markdown",
                        content=content, position=1)
    db_session.add(block)
    db_session.commit()
    return block


def test_fixed_fragments_are_in_current_course_and_stale_ones_are_not():
    course = AMPCR_COURSE_MARKDOWN["MC04"]
    for stale, fixed in MC04_SMART_FRAGMENTS:
        assert fixed in course
        assert stale not in course
        assert stale not in fixed


def test_stale_course_lacks_the_smart_expansion():
    assert SMART_EXPANSION not in _stale_course()


def test_repair_restores_the_current_course_and_is_idempotent(db_session):
    block = _make_block(db_session, "MC04", _stale_course())

    assert repair_mc04_smart_expansion(db_session) == 1
    db_session.commit()
    db_session.refresh(block)
    assert block.content == AMPCR_COURSE_MARKDOWN["MC04"]
    assert block.content.count(SMART_EXPANSION) == 3

    assert repair_mc04_smart_expansion(db_session) == 0


def test_repair_keeps_admin_edits_and_other_uaas(db_session):
    edited_text = "# MC04 réécrit depuis l'admin\n- **SMART** : texte modifié.\n"
    edited = _make_block(db_session, "MC04", edited_text)
    other = _make_block(db_session, "MC05", _stale_course())

    assert repair_mc04_smart_expansion(db_session) == 0
    db_session.refresh(edited)
    db_session.refresh(other)
    assert edited.content == edited_text
    assert SMART_EXPANSION not in other.content


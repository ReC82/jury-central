from app.ai.context import get_context


def test_get_context_returns_ampcr_mc01():
    context = get_context("ampcr-mc01")
    assert context is not None
    assert context.course_key == "ampcr-mc01"
    assert "PC" in context.course_title
    assert len(context.allowed_notions) >= 9
    assert len(context.competencies) == 4
    assert "RAM" in context.vocabulary
    assert "mini-cours 03" in context.constraints


def test_get_context_returns_none_for_unknown_key():
    assert get_context("does-not-exist") is None

"""Ticket #299 — consignes structurées des exercices pratiques AMPCR (contexte, documents,
données et règles, questions numérotées, sous-questions), sans changer la consigne
enregistrée, le barème ni la correction."""

import re

from app.seed import seed
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_COURSES,
    PRACTICAL_COURSES_BY_CODE,
    import_practical_bank,
)
from app.v1.models import QuestionnaireSession
from app.v1.prompt_layout import (
    ANNOTATIONS,
    _residual,
    layout_for_item,
    prompt_layout,
    validate_annotations,
)
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)
from tests.test_ticket233_ampcr_pratique_ex04 import SLUG, _ex04

ALL = [(course.code, item) for course in PRACTICAL_COURSES for item in course.items]


def _words(text: str) -> list[str]:
    return re.findall(r"\w+", text)


def test_annotations_are_exact_extracts():
    assert validate_annotations() == []


def test_every_practical_prompt_has_a_layout_and_nothing_is_lost():
    assert len({item.prompt for _c, item in ALL}) == len(ALL)  # retrouvé sans ambiguïté
    for code, item in ALL:
        layout = prompt_layout(item.prompt)
        assert layout is not None, (code, item.key)
        assert [s.text for s in layout.steps] == list(item.instructions)
        # Contexte = libellé de partie + contexte affiché + données et règles, mot pour mot.
        shown = " ".join((layout.label, layout.context, *layout.data_rules))
        assert sorted(_words(shown)) == sorted(_words(item.context)), (code, item.key)
        for step in layout.steps:
            if step.items:
                rest = _residual(step.text, (step.lead, *step.items))
                assert rest is not None and not re.search(r"\w", rest.replace(" et ", " ")), (code, item.key)


def test_unknown_prompt_keeps_original_display():
    assert prompt_layout(None) is None
    assert prompt_layout("Explique le rôle de la mémoire vive.") is None


def test_exam_part_label_and_data_rules():
    item = next(i for i in PRACTICAL_COURSES_BY_CODE["EX04"].items if i.key == "X02")
    layout = layout_for_item("EX04", item)
    assert layout.data_rules == ANNOTATIONS[("EX04", "X02")].data_rules
    assert all(rule not in layout.context for rule in layout.data_rules)
    assert layout.steps[0].lead.startswith("Pour chaque ligne a à d du document 3")
    assert len(layout.steps[0].items) == 6


def test_exam_session_pages_show_structured_prompt(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _ex04(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    seen_rules = False
    for position in range(1, session.question_count + 1):
        page = authenticated_client.get(f"{session_url}?q={position}").text
        assert 'class="jc-pl jc-pl-situation"' in page and "jc-q-prompt--structured" in page
        assert "Documents à consulter" in page  # chaque question EX04 a des documents
        anchors = re.findall(r'<a href="#(doc-q\d+)">', page)
        assert anchors and all(f'id="{a}"' in page for a in anchors)
        # Ordre : contexte → documents → données et règles → questions.
        assert page.index("jc-pl-situation") < page.index("jc-sd-stack") < page.index("jc-pl-questions")
        if "Données et règles" in page:
            seen_rules = True
            assert page.index("jc-sd-stack") < page.index("jc-pl-rules") < page.index("jc-pl-questions")
        assert "Corrigé de référence" not in page and "Barème" not in page
        assert "À faire :" not in page  # plus de bloc continu « … À faire : 1) … 2) … »
    assert seen_rules
    # La consigne enregistrée (envoyée au correcteur) reste celle d'origine.
    for sq in session.session_questions:
        assert prompt_layout(sq.question_version.content_json["prompt"]) is not None
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert html.count('class="jc-pl jc-pl-situation"') == session.question_count
    assert "data-score-on-100" in html


def test_other_subjects_keep_original_prompt(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr06", "practice")
    page = authenticated_client.get(f"{session_url}?q=1").text
    assert "jc-pl-situation" not in page and "jc-q-prompt-label" in page

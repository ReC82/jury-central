"""Ticket #148 — composition desktop des cours : plus de prose étroite dans une carte large.

Cause constatée sur le site (styles calculés, Chromium 1366 px) : `.jc-prose` portait
`max-width: 70ch` (~710 px) dans une carte de ~1060 px — FSE02 et FSE05-FSE16 gardaient un
grand vide à droite de la théorie. Correctif :
1. `.jc-prose` ne plafonne plus sa largeur ; la composition porte la largeur de lecture ;
2. théorie générique FSE05-16 : explication + colonne « Les mots clés » côte à côte ;
3. FSE02 : théorie recomposée en groupes pédagogiques (financements en cartes) ;
4. carte de texte seul : la carte entière prend une largeur de lecture (`.jc-card--reading`) ;
5. les blocs déjà seedés sont bien remplacés au prochain seed.
"""

import re
from pathlib import Path

from app import models
from app.content import is_text_only_html, render_markdown
from app.v1.course_memo import parse_html_definitions
from app.v1.fse02_course import fse02_course_sections, fse02_theory_html
from app.v1.fse05_course import fse05_course_sections
from app.v1.fse08_course import fse08_course_sections
from app.v1.fse12_course import fse12_course_sections

CSS = (Path(__file__).resolve().parents[1] / "app/static/css/design-system.css").read_text()


def _section(sections, suffix):
    return next(content for title, content in sections if title.endswith(suffix))


def _css_rule(selector: str) -> str:
    return CSS.split(selector + " {", 1)[1].split("}", 1)[0]


# --- 1. CSS --------------------------------------------------------------------------------


def test_prose_no_longer_caps_its_own_width():
    rule = _css_rule(".jc-prose")
    assert "70ch" not in rule
    assert "max-width: none" in rule
    assert "margin" not in rule


def test_theory_layout_two_columns_then_stacked_and_reading_card_rule():
    assert "grid-template-columns: minmax(0, 1.65fr) minmax(250px, 1fr)" in _css_rule(
        ".jc-theory-layout"
    )
    small = CSS.split("@media (max-width: 991.98px) {\n    .jc-theory-layout {", 1)[1]
    assert small.split("}", 1)[0].strip().startswith("grid-template-columns: 1fr")
    reading = _css_rule("#jc-lesson .jc-card--reading")
    assert "max-width: 50rem" in reading
    assert "margin-left: auto" in reading and "margin-right: auto" in reading


# --- 2. Théorie générique FSE05-16 ---------------------------------------------------------


def test_generic_theory_puts_prose_and_keywords_side_by_side():
    html = _section(fse05_course_sections(), "Théorie : notions et définitions")
    assert html.startswith('<div class="jc-theory-layout">')
    main, aside = html.split('<aside class="jc-theory-layout-aside"', 1)
    assert '<div class="jc-prose">' in main and "jc-definition-term" not in main
    assert "Les mots clés" in aside and aside.count('class="jc-definition"') == 9


def test_diagram_stays_full_width_below_the_layout():
    html = _section(fse08_course_sections(), "Théorie : notions et définitions")
    layout_end = html.index("</aside>\n</div>")
    assert html.index('<div class="jc-diagram"') > layout_end


def test_many_definitions_widen_the_keywords_column():
    fse12 = _section(fse12_course_sections(), "Théorie : notions et définitions")
    fse05 = _section(fse05_course_sections(), "Théorie : notions et définitions")
    assert "jc-theory-layout--wide-aside" in fse12
    assert "jc-theory-layout--wide-aside" not in fse05


# --- 3. FSE02 : groupes pédagogiques ----------------------------------------------------------


def test_fse02_theory_is_composed_in_pedagogical_groups():
    html = fse02_theory_html()
    titles = re.findall(r'<h3 class="jc-theory-group-title">.*?</span> (.+?)</h3>', html)
    assert titles == [
        "Média et offre médiatique",
        "L'interactivité",
        "Quatre modes de financement",
        "Le financement influence le média",
        "Un flux économique entre agents",
    ]
    assert html.count('class="jc-definition jc-fund-card"') == 4
    assert "jc-prose" not in html
    assert _section(fse02_course_sections(), "Théorie : notions et définitions") == html


def test_fse02_keeps_nuances_and_every_definition():
    html = fse02_theory_html()
    for nuance in ("financement MIXTE", "souvent combinés", "semaine suivante",
                   "EXCLUSIVEMENT par des fonds publics", "FSE15", "Qui verse à qui ?"):
        assert nuance in html
    terms = [card.term for card in parse_html_definitions(html)]
    assert terms == [
        "Média", "Offre médiatique", "Interactivité", "Vente", "Abonnement",
        "Publicité (comme mode de financement)", "Fonds publics", "Audience",
    ]
    rendered = render_markdown(html)
    assert "**" not in rendered and rendered.count("<aside") == 3


# --- 4. Carte de texte seul ----------------------------------------------------------------


def test_text_only_detection():
    assert is_text_only_html("<p>Un <strong>texte</strong>.</p>\n<ol><li>a</li></ol>")
    for html in ("<table><tr><td>x</td></tr></table>", '<div class="jc-definitions"></div>',
                 "<h2>Section</h2><p>x</p>", "<p><img src='x.png'></p>", ""):
        assert not is_text_only_html(html)


def test_course_page_reading_card_and_wide_theory(client, db_session):
    from app.seed import seed

    seed()
    text = client.get("/uaa/fse-fse02").text
    cards = re.findall(r'<div class="jc-card jc-card--(\w+) ([^"]*)">\s*.*?<h2 class="jc-card-title h5">(.*?)</h2>',
                       text, re.DOTALL)
    by_title = {title: extra.strip() for _, extra, title in cards}
    assert by_title["FSE02 — Présentation et objectifs"] == "jc-card--reading"
    assert by_title["FSE02 — Méthode"] == "jc-card--reading"
    assert by_title["FSE02 — Théorie : notions et définitions"] == ""
    assert "Quatre modes de financement" in text
    # La séquence « À retenir » relit toujours les définitions de la théorie recomposée
    assert "Offre médiatique" in text.split('id="a-retenir"', 1)[-1]


# --- 5. Actualisation des blocs déjà seedés --------------------------------------------------


def test_seed_refreshes_already_seeded_theory_blocks(client, db_session):
    from app.seed import seed

    seed()
    for slug, title in (("fse-fse02", "FSE02 — Théorie : notions et définitions"),
                        ("fse-fse03", "FSE03 — Qui suis-je ?"),
                        ("fse-fse05", "FSE05 — Théorie : notions et définitions")):
        uaa = db_session.query(models.UAA).filter_by(slug=slug).one()
        block = db_session.query(models.LessonBlock).filter_by(uaa_id=uaa.id, title=title).one()
        block.content = '<div class="jc-prose">\n<p>Ancien contenu pré-ticket #148.</p>\n</div>'
    db_session.commit()

    seed()
    db_session.expire_all()
    for title in ("FSE02 — Théorie : notions et définitions", "FSE03 — Qui suis-je ?",
                  "FSE05 — Théorie : notions et définitions"):
        blocks = db_session.query(models.LessonBlock).filter_by(title=title).all()
        assert len(blocks) == 1
        assert "pré-ticket #148" not in blocks[0].content
        assert "jc-theory-" in blocks[0].content

"""Ticket #124 — corrige l'effet « colonne étroite, moitié droite vide » introduit par
.jc-prose (ticket #120) : centrage générique (tous les cours qui l'utilisent), et mise en
page bespoke à deux colonnes pour FSE04 (flagship), avec comparaison à trois éléments
(valeur/norme/comportement) et un schéma montrant leur enchaînement. Vérifie aussi, comme
pour FSE03 (ticket #120), la resynchronisation de position des blocs existants après le
passage d'un bloc théorique unique à trois cartes."""

from pathlib import Path

from app.content import render_markdown
from app.v1.fse04_course import fse04_course_sections

CSS_PATH = Path(__file__).resolve().parents[1] / "app" / "static" / "css" / "design-system.css"


def _css_text() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


# =============================================================================================
# 1. CSS — le correctif générique (centrage) et les nouveaux composants existent bien
# =============================================================================================


def test_jc_prose_is_centered_not_just_width_limited():
    css = _css_text()
    prose_rule = css.split(".jc-prose {", 1)[1].split("}", 1)[0]
    assert "max-width: 70ch" in prose_rule
    assert "margin-left: auto" in prose_rule
    assert "margin-right: auto" in prose_rule


def test_theory_split_and_three_way_compare_components_exist():
    css = _css_text()
    assert ".jc-theory-split {" in css
    assert ".jc-theory-split-aside {" in css
    assert ".jc-compare--three {" in css
    assert ".jc-compare-item--c {" in css


def test_theory_split_stacks_to_one_column_on_small_screens():
    css = _css_text()
    assert "@media (max-width: 768px)" in css
    block = css.split("@media (max-width: 768px) {", 1)[1].split("}\n}", 1)[0]
    assert ".jc-theory-split" in block
    assert "grid-template-columns: 1fr" in block


# =============================================================================================
# 2. FSE04 — trois cartes bespoke, mise en page à deux colonnes, rien perdu
# =============================================================================================


def _sections_by_title():
    return dict(fse04_course_sections())


def test_old_merged_theory_block_replaced_by_three_cards():
    sections = _sections_by_title()
    assert "FSE04 — Théorie : notions et définitions" not in sections
    assert "FSE04 — Valeur, norme, comportement : quelle différence ?" in sections
    assert "FSE04 — Pourquoi suit-on parfois le groupe ?" in sections
    assert "FSE04 — Peut-on agir autrement ?" in sections


def test_sections_order_preserved():
    titles = [title for title, _ in fse04_course_sections()]
    assert titles == [
        "FSE04 — Présentation et objectifs",
        "FSE04 — Valeur, norme, comportement : quelle différence ?",
        "FSE04 — Pourquoi suit-on parfois le groupe ?",
        "FSE04 — Peut-on agir autrement ?",
        "FSE04 — Méthode",
        "FSE04 — Exemples commentés",
        "FSE04 — Comparer pour ne pas confondre",
        "FSE04 — Exercices guidés",
        "FSE04 — Fiche mémo",
    ]


def test_no_raw_markdown_leak_in_new_theory_cards():
    sections = _sections_by_title()
    for title in (
        "FSE04 — Valeur, norme, comportement : quelle différence ?",
        "FSE04 — Pourquoi suit-on parfois le groupe ?",
        "FSE04 — Peut-on agir autrement ?",
    ):
        html = render_markdown(sections[title])
        assert "**" not in html, f"fuite Markdown dans {title!r}"
        assert "<strong>" in html


def test_first_card_uses_three_way_compare_and_flow():
    html = render_markdown(
        _sections_by_title()["FSE04 — Valeur, norme, comportement : quelle différence ?"]
    )
    assert 'class="jc-compare jc-compare--three"' in html
    for item in ("Valeur", "Norme", "Comportement"):
        assert item in html
    assert '<div class="jc-flow">' in html


def test_second_card_uses_two_column_split_with_concrete_situation():
    html = render_markdown(
        _sections_by_title()["FSE04 — Pourquoi suit-on parfois le groupe ?"]
    )
    assert '<div class="jc-theory-split">' in html
    assert '<div class="jc-theory-split-main">' in html
    assert '<div class="jc-theory-split-aside">' in html
    assert "Situation concrète" in html
    # le texte original (ticket #97) reste intact dans la situation concrète
    assert "par désir de s'intégrer ou de ne pas se démarquer" in html


def test_all_eight_original_definitions_still_present():
    html = render_markdown(_sections_by_title()["FSE04 — Peut-on agir autrement ?"])
    assert '<details class="jc-glossary">' in html
    for term in (
        "Valeur", "Norme", "Comportement", "Besoin", "Frustration",
        "Groupe d'appartenance", "Influence sociale", "Socialisation",
    ):
        assert term in html


def test_definitions_already_visible_before_glossary_not_only_hidden_there():
    """Chaque terme doit déjà apparaître dans les explications visibles (pas seulement
    dans le lexique replié) — même exigence que FSE03 (ticket #120)."""
    card1 = render_markdown(
        _sections_by_title()["FSE04 — Valeur, norme, comportement : quelle différence ?"]
    )
    for term in ("Valeur", "Norme", "Comportement"):
        assert term in card1

    card2 = render_markdown(_sections_by_title()["FSE04 — Pourquoi suit-on parfois le groupe ?"])
    for term in ("besoins", "groupe d'appartenance", "influence sociale", "socialisation"):
        assert term.split()[0].lower() in card2.lower()

    card3 = render_markdown(_sections_by_title()["FSE04 — Peut-on agir autrement ?"])
    assert "frustration" in card3.lower()


def test_full_fse04_page_still_contains_required_exam_notions(client, db_session):
    from app.seed import seed

    seed()
    response = client.get("/uaa/fse-fse04")
    assert response.status_code == 200
    text = response.text
    for notion in (
        "norme", "valeur", "comportement", "influence sociale", "socialisation",
        "frustration", "responsabilité individuelle",
    ):
        assert notion in text
    assert "Karim" in text
    assert "provisoire" not in text.lower()


# =============================================================================================
# 3. Resynchronisation de position (même bug que FSE03, ticket #120, reproduit ici pour
#    FSE04 avant qu'il ne se manifeste en production)
# =============================================================================================


def test_reseed_on_pre_ticket124_state_fixes_block_order_without_duplication(db_session):
    from app.models import UAA, BlockSpace, BlockType, LessonBlock, Module
    from app.seed import seed
    from app.v1.fse_plan import FSE_MODULE_CODE

    seed()

    uaa = db_session.query(UAA).join(Module).filter(
        Module.code == FSE_MODULE_CODE, UAA.code == "FSE04"
    ).first()
    blocks = {b.title: b for b in db_session.query(LessonBlock).filter_by(uaa_id=uaa.id).all()}

    for title in (
        "FSE04 — Valeur, norme, comportement : quelle différence ?",
        "FSE04 — Pourquoi suit-on parfois le groupe ?",
        "FSE04 — Peut-on agir autrement ?",
    ):
        db_session.delete(blocks[title])
    db_session.add(
        LessonBlock(
            uaa=uaa,
            title="FSE04 — Théorie : notions et définitions",
            type=BlockType.MARKDOWN,
            content="Ancien contenu fusionné (pré-ticket #124).",
            position=2,
            is_published=True,
            space=BlockSpace.COURSE,
        )
    )
    blocks["FSE04 — Méthode"].position = 3
    blocks["FSE04 — Comparer pour ne pas confondre"].position = 5
    blocks["FSE04 — Fiche mémo"].position = 7
    db_session.commit()

    seed()

    refreshed = db_session.query(LessonBlock).filter_by(uaa_id=uaa.id).all()
    by_title = {b.title: b for b in refreshed}
    assert "FSE04 — Théorie : notions et définitions" not in by_title

    positions = {b.title: b.position for b in refreshed}
    assert len(set(positions.values())) == len(positions), f"collision de position : {positions}"

    ordered_titles = [b.title for b in sorted(refreshed, key=lambda b: b.position)]
    assert ordered_titles == [
        "FSE04 — Présentation et objectifs",
        "FSE04 — Valeur, norme, comportement : quelle différence ?",
        "FSE04 — Pourquoi suit-on parfois le groupe ?",
        "FSE04 — Peut-on agir autrement ?",
        "FSE04 — Méthode",
        "FSE04 — Exemples commentés",
        "FSE04 — Comparer pour ne pas confondre",
        "FSE04 — Exercices guidés",
        "FSE04 — Fiche mémo",
    ]

"""Ticket #126 — corrige la composition de la théorie FSE après retour visuel réel sur le
site (pas seulement le centrage introduit au ticket #124, jugé insuffisant) :

1. `.jc-prose` n'est plus centré (`margin: 0 auto` retiré) : il partage désormais le même
   repère gauche que le titre de la carte et tout ce qui l'entoure, au lieu de « flotter »
   au centre d'une carte plus large.
2. FSE04 « Peut-on agir autrement ? » : la colonne de prose isolée devient deux cartes de
   largeur égale (`.jc-theory-cards`/`.jc-theory-card`, icône + titre + paragraphes courts,
   fond discret, sans bordure propre), suivies d'un encadré « À retenir » compact au texte
   simplifié imposé, puis du lexique inchangé.
3. `.jc-compare--three` et `.jc-theory-cards` utilisent un nombre de colonnes FIXE
   (`repeat(N, 1fr)` + media query), pas `repeat(auto-fit, minmax(...))` (ticket #124) :
   cette dernière technique collapsait systématiquement sur une seule colonne avec l'outil
   de prévisualisation locale (WeasyPrint), reproduit en isolation avant correctif — voir
   le commentaire CSS. Vérifié ici pour ne pas régresser vers l'ancienne technique."""

from pathlib import Path

from app.content import render_markdown
from app.v1.fse04_course import fse04_course_sections

CSS_PATH = Path(__file__).resolve().parents[1] / "app" / "static" / "css" / "design-system.css"


def _css_text() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


def _css_rule(selector: str) -> str:
    return _css_text().split(selector + " {", 1)[1].split("}", 1)[0]


# =============================================================================================
# 1. CSS — plus de centrage, colonnes fixes (jamais auto-fit) pour les grilles à 2/3
# =============================================================================================


def test_jc_prose_not_centered():
    rule = _css_rule(".jc-prose")
    assert "margin" not in rule


def test_theory_cards_and_three_way_compare_use_fixed_columns_never_auto_fit():
    cards_rule = _css_rule(".jc-theory-cards")
    assert "grid-template-columns: repeat(2, 1fr)" in cards_rule
    assert "auto-fit" not in cards_rule
    three_rule = _css_rule(".jc-compare--three")
    assert "grid-template-columns: repeat(3, 1fr)" in three_rule
    assert "auto-fit" not in three_rule


def test_theory_cards_component_exists_with_discreet_background_no_border():
    css = _css_text()
    assert ".jc-theory-cards {" in css
    card_rule = _css_rule(".jc-theory-card")
    assert "var(--jc-gray-bg)" in card_rule
    assert "border:" not in card_rule
    assert "border-color" not in card_rule
    assert "border-width" not in card_rule
    assert ".jc-theory-card-icon {" in css
    assert ".jc-theory-card-title {" in css


def test_theory_cards_stack_to_one_column_on_phone():
    css = _css_text()
    assert "@media (max-width: 576px)" in css
    # la règle doit viser .jc-theory-cards quelque part dans une media query 576px
    blocks = css.split("@media (max-width: 576px) {")[1:]
    assert any(".jc-theory-cards" in b.split("}\n}", 1)[0] for b in blocks)


def test_theory_cards_avoids_page_break_at_print():
    css = _css_text()
    assert "@media print" in css
    blocks = css.split("@media print {")[1:]
    assert any(".jc-theory-cards" in b.split("}\n}", 1)[0] for b in blocks)


# =============================================================================================
# 2. FSE04 « Peut-on agir autrement ? » — deux cartes + encadré compact + lexique
# =============================================================================================


def _section3_html() -> str:
    sections = dict(fse04_course_sections())
    return render_markdown(sections["FSE04 — Peut-on agir autrement ?"])


def test_isolated_prose_column_is_gone():
    html = _section3_html()
    assert '<div class="jc-prose">' not in html


def test_two_cards_with_exact_titles_and_icons():
    html = _section3_html()
    assert html.count('<div class="jc-theory-card">') == 2
    assert "Une tension peut créer de la frustration" in html
    assert "Le groupe influence, chacun peut réagir" in html
    assert '<span class="jc-theory-card-icon"' in html


def test_takeaway_text_matches_exact_requested_sentence():
    html = _section3_html()
    assert "Le groupe peut influencer nos comportements. Chacun reste responsable de ses actes." in html


def test_nuance_preserved_in_cards_even_though_takeaway_is_simplified():
    """La phrase de synthèse de l'encadré est volontairement simple, mais la nuance
    (tendance statistique ≠ fatalité individuelle) reste expliquée dans la carte."""
    html = _section3_html()
    assert "tendance statistique" in html
    assert "jamais une fatalité individuelle" in html
    assert "frustration" in html.lower()


def test_glossary_still_present_and_unchanged_below():
    html = _section3_html()
    assert '<details class="jc-glossary">' in html
    for term in (
        "Valeur", "Norme", "Comportement", "Besoin", "Frustration",
        "Groupe d'appartenance", "Influence sociale", "Socialisation",
    ):
        assert term in html


def test_no_markdown_leak():
    html = _section3_html()
    assert "**" not in html
    assert "<strong>" in html


def test_full_fse04_page_still_contains_required_exam_notions(client, db_session):
    from app.seed import seed

    seed()
    response = client.get("/uaa/fse-fse04")
    assert response.status_code == 200
    text = response.text
    for notion in (
        "norme", "valeur", "comportement", "influence sociale", "socialisation",
        "frustration", "responsabilité",
    ):
        assert notion in text
    assert "provisoire" not in text.lower()
    assert "jc-theory-cards" in text

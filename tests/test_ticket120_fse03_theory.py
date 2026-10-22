"""Ticket #120 — FSE03 : le bloc théorique unique « Théorie : notions et définitions » est
remplacé par trois cartes progressives (« Qui suis-je ? », « Quelles traces je laisse ? »,
« Quelle image les autres voient-ils ? »), plus un lexique repliable reprenant les 7
définitions d'origine (ticket #97) sans qu'aucune ne soit perdue. Vérifie aussi que le HTML
littéral ne laisse fuiter aucune syntaxe Markdown (diagnostic ticket #112) et que la
nuance « ancienne publication volontaire ≠ devenue involontaire » est bien présente."""

from app.content import render_markdown
from app.v1.fse03_course import fse03_course_sections


def _sections_by_title():
    return dict(fse03_course_sections())


def test_old_merged_theory_block_is_replaced_by_three_progressive_cards():
    sections = _sections_by_title()
    assert "FSE03 — Théorie : notions et définitions" not in sections
    assert "FSE03 — Qui suis-je ?" in sections
    assert "FSE03 — Quelles traces je laisse ?" in sections
    assert "FSE03 — Quelle image les autres voient-ils ?" in sections


def test_theory_cards_order_preserved_around_new_sections():
    titles = [title for title, _ in fse03_course_sections()]
    assert titles == [
        "FSE03 — Présentation et objectifs",
        "FSE03 — Qui suis-je ?",
        "FSE03 — Quelles traces je laisse ?",
        "FSE03 — Quelle image les autres voient-ils ?",
        "FSE03 — Méthode",
        "FSE03 — Exemples commentés",
        "FSE03 — Comparer pour ne pas confondre",
        "FSE03 — Exercices guidés",
        "FSE03 — Fiche mémo",
    ]


def test_no_raw_markdown_bold_leaks_in_theory_cards():
    sections = _sections_by_title()
    for title in (
        "FSE03 — Qui suis-je ?",
        "FSE03 — Quelles traces je laisse ?",
        "FSE03 — Quelle image les autres voient-ils ?",
    ):
        html = render_markdown(sections[title])
        assert "**" not in html, f"fuite Markdown dans {title!r}"
        assert "<strong>" in html


def test_all_seven_original_definitions_still_present_in_glossary():
    html = render_markdown(_sections_by_title()["FSE03 — Quelle image les autres voient-ils ?"])
    assert '<details class="jc-glossary">' in html
    assert "Retrouver les définitions" in html
    for term in (
        "Identité personnelle",
        "Identité collective",
        "Groupe d'appartenance",
        "Identité numérique",
        "Trace numérique volontaire",
        "Trace numérique involontaire",
        "Réputation",
    ):
        assert term in html


def test_voluntary_old_publication_nuance_is_explicit():
    html = render_markdown(_sections_by_title()["FSE03 — Quelles traces je laisse ?"])
    assert "<blockquote>" in html
    assert "ne devient pas automatiquement" in html
    assert "visibilité ultérieure" in html


def test_identity_definitions_already_visible_before_glossary():
    """Les définitions doivent déjà figurer dans les explications visibles (pas seulement
    dans le lexique replié) — § 3 du ticket #120."""
    identity_html = render_markdown(_sections_by_title()["FSE03 — Qui suis-je ?"])
    assert "Identité personnelle" in identity_html
    assert "Identité collective" in identity_html
    assert "identité numérique" in identity_html.lower()

    traces_html = render_markdown(_sections_by_title()["FSE03 — Quelles traces je laisse ?"])
    assert "Trace volontaire" in traces_html
    assert "Trace involontaire" in traces_html

    image_html = render_markdown(_sections_by_title()["FSE03 — Quelle image les autres voient-ils ?"])
    assert "réputation" in image_html.lower()


def test_reputation_flow_diagram_present_with_three_steps():
    html = render_markdown(_sections_by_title()["FSE03 — Quelle image les autres voient-ils ?"])
    assert '<div class="jc-flow">' in html
    for step in ("Traces visibles", "Perception des autres", "Réputation"):
        assert step in html


def test_full_fse03_page_still_contains_required_exam_notions(client, db_session):
    from app.seed import seed

    seed()
    response = client.get("/uaa/fse-fse03")
    assert response.status_code == 200
    text = response.text
    for notion in (
        "identité numérique", "trace", "volontaire", "involontaire", "réputation",
        "appartenance", "identité réelle", "image",
    ):
        assert notion in text
    assert "provisoire" not in text.lower()


def test_reseed_on_pre_ticket120_state_fixes_block_order_without_duplication(db_session):
    """Reproduit le bug trouvé en production lors de l'installation du ticket #120 : sur
    un staging déjà seedé AVANT ce ticket, "Méthode"/"Comparer pour ne pas confondre"/
    "Fiche mémo" existent déjà avec leur ANCIENNE position (jamais dans `obsolete_titles`,
    donc jamais recréés) — sans `reposition_titles=FSE03_REPOSITION_TITLES`, un second
    `seed()` les laisserait en collision de position avec les trois nouveaux blocs de
    théorie, inversant l'ordre d'affichage (Fiche mémo avant Exercices guidés)."""
    from app.models import UAA, BlockSpace, BlockType, LessonBlock, Module
    from app.seed import seed
    from app.v1.fse_plan import FSE_MODULE_CODE

    seed()

    uaa = db_session.query(UAA).join(Module).filter(
        Module.code == FSE_MODULE_CODE, UAA.code == "FSE03"
    ).first()
    blocks = {b.title: b for b in db_session.query(LessonBlock).filter_by(uaa_id=uaa.id).all()}

    # Simule l'état d'un staging seedé juste avant le ticket #120 : ancien bloc fusionné
    # (position 2), et les trois blocs suivants remis à leurs anciennes positions.
    for title in (
        "FSE03 — Qui suis-je ?",
        "FSE03 — Quelles traces je laisse ?",
        "FSE03 — Quelle image les autres voient-ils ?",
    ):
        db_session.delete(blocks[title])
    db_session.add(
        LessonBlock(
            uaa=uaa,
            title="FSE03 — Théorie : notions et définitions",
            type=BlockType.MARKDOWN,
            content="Ancien contenu fusionné (pré-ticket #120).",
            position=2,
            is_published=True,
            space=BlockSpace.COURSE,
        )
    )
    blocks["FSE03 — Méthode"].position = 3
    blocks["FSE03 — Comparer pour ne pas confondre"].position = 5
    blocks["FSE03 — Fiche mémo"].position = 7
    db_session.commit()

    seed()

    refreshed = db_session.query(LessonBlock).filter_by(uaa_id=uaa.id).all()
    by_title = {b.title: b for b in refreshed}
    assert "FSE03 — Théorie : notions et définitions" not in by_title

    positions = {b.title: b.position for b in refreshed}
    assert len(set(positions.values())) == len(positions), f"collision de position : {positions}"

    ordered_titles = [b.title for b in sorted(refreshed, key=lambda b: b.position)]
    assert ordered_titles == [
        "FSE03 — Présentation et objectifs",
        "FSE03 — Qui suis-je ?",
        "FSE03 — Quelles traces je laisse ?",
        "FSE03 — Quelle image les autres voient-ils ?",
        "FSE03 — Méthode",
        "FSE03 — Exemples commentés",
        "FSE03 — Comparer pour ne pas confondre",
        "FSE03 — Exercices guidés",
        "FSE03 — Fiche mémo",
    ]

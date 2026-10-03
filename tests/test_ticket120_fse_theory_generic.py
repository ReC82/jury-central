"""Ticket #120 — restructuration générique de la théorie des cours FSE02/FSE04-FSE16 (ceux
qui partagent `app.v1.fse_course_sections.build_course_sections`) : la prose devient du
HTML littéral à largeur de lecture limitée (`.jc-prose`), les définitions deviennent des
cartes `.jc-definitions` (repliées en `.jc-glossary` seulement si elles répètent déjà la
prose visible, jamais sinon). Vérifie l'absence de fuite Markdown (diagnostic ticket #112),
la non-perte de matière (chaque terme défini reste présent quelque part dans le texte
affiché) et le cas particulier d'un terme groupé (ex. FSE08 "Région (flamande, wallonne,
Bruxelles-Capitale)") jamais découpé à l'intérieur."""

import re

import pytest

from app.content import render_markdown
from app.v1.fse_course_sections import (
    _definitions_bullets_to_items,
    parse_numbered_sections,
    theory_and_definitions_to_cards,
    theory_prose_to_html,
)

GENERIC_COURSES = [
    "fse02", "fse04", "fse05", "fse06", "fse07", "fse08", "fse09", "fse10",
    "fse11", "fse12", "fse13", "fse14", "fse15", "fse16",
]


def _course_markdown(code: str) -> str:
    import importlib

    module = importlib.import_module(f"app.v1.{code}_course")
    fn = getattr(module, f"{code}_course_markdown")
    return fn()


# =============================================================================================
# 1. Fonctions unitaires — cas construits, sans dépendre du contenu réel d'un cours
# =============================================================================================


def test_theory_prose_to_html_converts_bold_and_wraps_in_prose_div():
    html = theory_prose_to_html("Un **terme** important.\n\nUn second paragraphe.")
    assert "**" not in html
    assert "<strong>terme</strong>" in html
    assert '<div class="jc-prose">' in html
    assert html.count('<div class="jc-prose">') == 1  # un seul bloc contigu de prose


def test_theory_prose_to_html_splits_inline_list_without_blank_line():
    raw = "Phrase d'intro avec une liste :\n- premier **élément** ;\n- second élément."
    html = theory_prose_to_html(raw)
    assert "<ul>" in html
    assert "<li>premier <strong>élément</strong> ;</li>" in html
    assert "- premier" not in html  # jamais de tiret littéral


def test_theory_prose_to_html_passes_raw_html_block_through_unwrapped_and_outside_prose():
    raw = "Un paragraphe avant.\n\n<div class=\"jc-diagram\">contenu</div>\n\nUn paragraphe après."
    html = theory_prose_to_html(raw)
    assert '<p><div class="jc-diagram">contenu</div></p>' not in html
    assert '<div class="jc-diagram">contenu</div>' in html
    # le schéma n'est jamais à l'intérieur d'un .jc-prose (il a besoin de toute la largeur)
    prose_divs = re.findall(r'<div class="jc-prose">.*?</div>', html, re.DOTALL)
    assert all("jc-diagram" not in d for d in prose_divs)


def test_definitions_bullets_never_split_a_grouped_term():
    raw = "- **Région** (flamande, wallonne, Bruxelles-Capitale) : compétences territoriales."
    items = _definitions_bullets_to_items(raw)
    assert items == [
        (
            "Région (flamande, wallonne, Bruxelles-Capitale)",
            "compétences territoriales.",
        )
    ]


def test_definitions_become_visible_grid_when_not_fully_redundant():
    theory = "On explique la vente et l'abonnement ici."
    definitions = (
        "- **Vente** : paiement à l'unité.\n"
        "- **Terme inédit** : jamais mentionné ailleurs."
    )
    html = theory_and_definitions_to_cards(theory, definitions)
    assert '<div class="jc-definitions">' in html
    assert "<details" not in html  # pas caché : un terme n'est pas redondant


def test_definitions_become_glossary_when_fully_redundant():
    theory = "On explique la vente ici, et l'abonnement aussi."
    definitions = (
        "- **Vente** : paiement à l'unité.\n"
        "- **Abonnement** : paiement régulier."
    )
    html = theory_and_definitions_to_cards(theory, definitions)
    assert '<details class="jc-glossary">' in html
    assert "Retrouver les définitions" in html


# =============================================================================================
# 2. Les 14 cours réels (FSE02/FSE04-FSE16) — aucune perte de matière, aucune fuite
# =============================================================================================


@pytest.mark.parametrize("code", GENERIC_COURSES)
def test_no_markdown_leak_and_no_content_loss(code):
    sections = parse_numbered_sections(_course_markdown(code))
    theory_raw, definitions_raw = sections[2], sections[3]
    html = render_markdown(theory_and_definitions_to_cards(theory_raw, definitions_raw))

    assert "**" not in html, f"fuite Markdown dans {code}"
    assert html.count("<p>-") == 0 and "\n-" not in re.sub(r"<li>.*?</li>", "", html, flags=re.DOTALL)

    items = _definitions_bullets_to_items(definitions_raw)
    assert items, f"{code} : aucune définition reconnue (regex à revoir ?)"
    for term, _ in items:
        bare_term = term.split("(")[0].strip()
        assert bare_term in html, f"{code} : terme {bare_term!r} absent du rendu"


@pytest.mark.parametrize("code", GENERIC_COURSES)
def test_theory_block_title_unchanged(code):
    """Le titre du bloc reste identique (pas de scission en plusieurs blocs comme FSE03,
    donc aucune resynchronisation de position n'est nécessaire dans `app.seed`)."""
    from app.v1.fse_course_sections import build_course_sections

    sections = dict(build_course_sections(code.upper(), _course_markdown(code)))
    assert f"{code.upper()} — Théorie : notions et définitions" in sections


# =============================================================================================
# 3. Un aller-retour HTTP réel par cours — la page se charge et garde ses notions d'examen
# =============================================================================================


@pytest.mark.parametrize("code", GENERIC_COURSES)
def test_course_page_loads_with_restructured_theory(client, db_session, code):
    from app.seed import seed

    seed()
    response = client.get(f"/uaa/fse-{code}")
    assert response.status_code == 200
    text = response.text
    assert "provisoire" not in text.lower()
    assert "jc-prose" in text
    assert "jc-definitions" in text

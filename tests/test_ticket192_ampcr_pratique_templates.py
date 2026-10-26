"""Ticket #192 (reprise du 26/10) — numérotation alignée sur les tickets du propriétaire,
schémas SVG vérifiables et modèles de tickets PR01–PR30 / EX01–EX06. Aucune IA."""

import re
from dataclasses import replace
from pathlib import Path

import pytest

from app.v1 import ampcr_pratique_plan as plan
from app.v1 import ampcr_pratique_tickets as tickets
from app.v1.ampcr_pratique_format import EXAMPLE_EXERCISE, EXAMPLE_FIGURES, EXAMPLE_PC_SIDE
from app.v1.ampcr_pratique_visuals import (
    DIAGNOSTIC_METHOD_FIGURE,
    T568A,
    T568B,
    Figure,
    connector_pins_svg,
    pin_table,
    render_figure,
    validate_figure,
)

DOC = Path(__file__).resolve().parent.parent / "docs" / "ampcr_pratique_tickets.md"


# --- Numérotation : les tickets déjà rédigés font foi ---------------------------------------


@pytest.mark.parametrize(
    ("code", "issue", "keyword", "requirement"),
    [
        ("PR06", 193, "pannes matérielles", "AP-15"),
        ("PR11", 194, "Messages d'erreur", "AP-13"),
        ("PR15", 197, "RJ45", "AP-34"),
    ],
)
def test_owner_tickets_keep_their_code(code, issue, keyword, requirement):
    course = plan.COURSE_SLOTS_BY_CODE[code]
    assert keyword in course.title
    assert requirement in course.requirement_ids
    assert tickets.EXISTING_TICKETS[code] == issue


def test_plan_still_covers_every_requirement_with_30_courses_in_order():
    assert [c.code for c in plan.COURSE_SLOTS] == [f"PR{i:02d}" for i in range(1, 31)]
    for module in plan.MODULES:
        assert module.course_codes, module.key
    for requirement in plan.ALL_REQUIREMENTS:
        assert plan.courses_for_requirement(requirement.id), requirement.id
        assert plan.exercises_for_requirement(requirement.id), requirement.id


# --- Données techniques des schémas ----------------------------------------------------------


def test_t568_pinouts_are_the_standard_ones():
    assert T568B == (
        "blanc-orange", "orange", "blanc-vert", "bleu",
        "blanc-bleu", "vert", "blanc-marron", "marron",
    )
    assert T568A == (
        "blanc-vert", "vert", "blanc-orange", "bleu",
        "blanc-bleu", "orange", "blanc-marron", "marron",
    )
    # A et B échangent les paires orange et verte (broches 1-2 ↔ 3-6) ; bleu et marron identiques.
    swap = {"orange": "vert", "vert": "orange", "blanc-orange": "blanc-vert",
            "blanc-vert": "blanc-orange"}
    assert tuple(swap.get(w, w) for w in T568B) == T568A
    for pin in (4, 5, 7, 8):
        assert T568A[pin - 1] == T568B[pin - 1]


def test_connector_svg_draws_each_pin_from_data_in_order():
    svg = connector_pins_svg(T568B, label="T568B")
    assert re.findall(r'data-pin="(\d)" data-wire="([a-z-]+)"', svg) == [
        (str(pin), wire) for pin, wire in pin_table(T568B)
    ]
    assert "viewBox=" in svg
    with pytest.raises(ValueError):
        connector_pins_svg(T568B[:7], label="7 broches")
    with pytest.raises(ValueError):
        connector_pins_svg(T568B[:7] + ("rouge",), label="couleur inconnue")


def test_example_schema_matches_table_and_correction():
    # Côté PC : seules les broches 4 et 6 diffèrent de T568B (vert en 4, bleu en 6).
    differing = [i + 1 for i, (a, b) in enumerate(zip(EXAMPLE_PC_SIDE, T568B, strict=True)) if a != b]
    assert differing == [4, 6]
    assert EXAMPLE_PC_SIDE[3] == "vert" and EXAMPLE_PC_SIDE[5] == "bleu"
    table = EXAMPLE_EXERCISE.documents[0].content_text
    assert ", ".join(EXAMPLE_PC_SIDE) in table and ", ".join(T568B) in table
    assert "fils 4 et 6" in table
    wall, pc = EXAMPLE_FIGURES
    assert ", ".join(T568B) in wall.alt and ", ".join(EXAMPLE_PC_SIDE) in pc.alt


# --- Accessibilité et garde-fous des figures -------------------------------------------------


def test_render_figure_is_accessible_and_flagged_non_official():
    html = str(render_figure(DIAGNOSTIC_METHOD_FIGURE))
    assert 'role="img"' in html
    assert '<title id="fig-demarche-intervention-title">' in html
    assert '<desc id="fig-demarche-intervention-desc">' in html
    assert "schéma non officiel" in html
    assert html.count("<text") >= 12  # 6 étapes : titre + au moins une ligne de détail


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"alt": "Schéma."}, "Texte alternatif"),
        ({"caption": " "}, "Légende"),
        ({"svg": "<svg><text>x</text></svg>"}, "viewBox"),
        ({"svg": '<svg viewBox="0 0 1 1"><script>alert(1)</script></svg>'}, "script"),
        ({"svg": '<svg viewBox="0 0 1 1" onload="x()"></svg>'}, "script"),
        ({"svg": '<svg viewBox="0 0 1 1"><image href="https://x/y.png"/></svg>'}, "externe"),
        ({"caption": "Schéma officiel du Jury"}, "officiel"),
    ],
)
def test_validate_figure_refuses_unsafe_or_incomplete_figures(change, message):
    figure = replace(DIAGNOSTIC_METHOD_FIGURE, **change)
    errors = validate_figure(figure)
    assert any(message in error for error in errors), errors
    with pytest.raises(ValueError):
        render_figure(figure)


def test_all_shipped_figures_are_valid():
    for figure in (*EXAMPLE_FIGURES, DIAGNOSTIC_METHOD_FIGURE):
        assert isinstance(figure, Figure)
        assert validate_figure(figure) == []


def test_format_page_shows_verified_schemas(client):
    response = client.get("/ampcr-pratique/format-exercice")
    assert response.status_code == 200
    html = response.text
    assert html.count('class="jc-tech-figure"') == 3
    assert re.findall(r'data-wire="([a-z-]+)"', html)[:16] == list(T568B) + list(EXAMPLE_PC_SIDE)
    assert "Démarche attendue dans une réponse écrite" in html
    assert "break-inside: avoid" in html


# --- Modèles de tickets ----------------------------------------------------------------------


def test_ticket_document_is_in_sync_with_plan():
    assert DOC.read_text(encoding="utf-8") == tickets.render_document(), (
        "Régénérer : python -m app.v1.ampcr_pratique_tickets > docs/ampcr_pratique_tickets.md"
    )


def test_every_course_and_exam_skeleton_carries_exact_requirements_and_contract():
    for course in plan.COURSE_SLOTS:
        text = tickets.course_ticket(course.code)
        assert f"[AMPCR pratique {course.code}]" in text
        for requirement_id in course.requirement_ids:
            assert plan.REQUIREMENTS_BY_ID[requirement_id].text in text
        assert "Matière obligatoire" in text
        assert "Contrat de fin de ticket" in text and "Email de fin de ticket" in text
        assert "SVG construit à partir de données" in text
    for module in plan.MODULES:
        for code in module.exercise_codes:
            exercise = plan.EXERCISE_SLOTS_BY_CODE[code]
            text = tickets.exam_ticket(code)
            assert ("PR01–PR30" if exercise.is_global else ", ".join(module.course_codes)) in text
            assert f"#{exercise.ticket}" in text
            assert "Aucune durée inventée" in text
            assert "Contrat de fin de ticket" in text
    assert "Ticket déjà rédigé : #193" in tickets.course_ticket("PR06")


def test_ticket_document_lists_36_skeletons_and_checklist():
    text = tickets.render_document()
    assert len(re.findall(r"^#### \[AMPCR pratique (?:PR|EX)\d\d\]", text, re.MULTILINE)) == 36
    assert "Checklist de validation éditoriale et visuelle" in text
    assert text.count("- [ ]") >= 15

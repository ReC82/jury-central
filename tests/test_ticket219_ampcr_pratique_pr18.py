"""Ticket #219 — AMPCR pratique écrite, PR18 « Installation physique d'un mini-réseau ».

Couvre : données de référence et calculs **recontrôlés ici** indépendamment (longueurs d'après le
plan, ports du switch, panneaux, baie, boîtes de câble, budget PoE, devis et TVA, repérage,
verdicts de recette, ordre de validation) ; schémas SVG (validité, accessibilité, données
dessinées, schémas à compléter sans leurs réponses, fichiers statiques) ; exercices et
mini-examen (format du socle, remises en ordre et classements auto-corrigés, nombres des
corrigés, 5 schémas à compléter et 4 devis) ; cours (matière du ticket, 3 procédures, 5 cas
résolus, liens, supports fictifs, cartes) ; banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

import math
import re
from html import escape
from pathlib import Path

import pytest

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_audit import proven_requirement_ids as audit_proven_ids
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    _document_layout,
    get_practical_context,
    import_practical_bank,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_pr18_bank import (
    E13_BOXES,
    E13_LENGTHS,
    E13_TOTAL_M,
    E14_HT,
    E14_TTC,
    E14_VAT,
    E15_CHOICE,
    E15_POE,
    E15_PORTS,
    E16_RACK,
    E16_USED,
    E17_BOXES,
    E17_LENGTHS,
    E17_TOTAL,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_ORDER,
    KIND_PLAN,
    KIND_QUOTE,
    KIND_SAFETY,
    KIND_SCHEMA,
    KIND_TEST,
    PLACE_AP,
    PLACE_BOX,
    PLACE_OUTLET,
    PLACE_PATH,
    PLACE_RACK,
    PRACTICE_ITEMS,
    REQ,
    X01_LENGTHS,
    X03_LINKS,
    X03_SWITCH,
    X04_HT,
    X04_TTC,
    X04_VAT,
    X05_TOTAL,
    validate_items,
)
from app.v1.ampcr_pratique_pr18_course import CASES, PR18_SLUG, PR18_TITLE, pr18_course_sections
from app.v1.ampcr_pratique_pr18_figures import (
    CHECK_STEPS,
    D_GW,
    D_IP,
    D_NET,
    D_OK,
    D_PEER,
    D_PHYS,
    D_SHARE,
    INSTALL_STEPS,
    PATCH_ROWS,
    PLAN,
    PLAN_BLANKS,
    PLAN_QUOTE,
    PLAN_QUOTE_TOTALS,
    PLAN_RUNS,
    POE_KO,
    POE_OK,
    PR18_FIGURES,
    PROCEDURES,
    RACK_LAYOUT,
    STATIC_FIGURES,
    T_LENGTH,
    T_OK,
    T_PERF,
    T_WIRING,
    TEST_STEPS,
    LinkTest,
    Point,
    QuoteLine,
    RackItem,
    boxes_needed,
    choose_rack,
    choose_switch,
    euro,
    first_failure,
    horizontal_m,
    label_for,
    link_verdict,
    min_separation_mm,
    panels_needed,
    poe_budget_w,
    poe_verdict,
    quote_totals,
    rack_svg,
    rack_units,
    run_length_m,
    static_svg,
    switch_ports_needed,
    validation_diagnosis,
)
from app.v1.ampcr_pratique_visuals import render_figure, validate_figure
from app.v1.models import Question, QuestionnaireSession, SessionMode
from app.v1.question_engine import validate_content
from app.v1.session_service import _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-pr18"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr18_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr18(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR18")
    return module, uaa


# =============================================================================================
# 1. Données de référence et calculs, recontrôlés indépendamment
# =============================================================================================


def test_lengths_from_the_plan():
    rack = PLAN.rack
    for key, horizontal, length in PLAN_RUNS:
        outlet = next(o for o in PLAN.outlets if o.key == key)
        assert horizontal == abs(outlet.x - rack.x) + abs(outlet.y - rack.y)
        assert length == math.ceil(horizontal + 5) and length <= 90
    assert horizontal_m(Point("A", "", 0, 0), Point("B", "", 3, 4)) == 7  # jamais la diagonale (5 m)
    assert run_length_m(10.0) == 15 and run_length_m(10.2) == 16 and run_length_m(87.5) == 93
    assert max(length for *_r, length in PLAN_RUNS) == 23 and len(PLAN.outlets) == 13
    # toutes les prises et la baie dans le bâtiment
    for point in (PLAN.rack, PLAN.box, *PLAN.outlets):
        assert 0 <= point.x <= PLAN.width_m and 0 <= point.y <= PLAN.depth_m
    assert [o.key for o in PLAN.outlets if o.poe_class] == ["P13"]


def test_sizing_switch_panels_rack_and_boxes():
    assert switch_ports_needed(13) == 17 and choose_switch(13) == 24  # 13 × 1,2 = 15,6 → 16, + box
    assert switch_ports_needed(10) == 13 and choose_switch(10) == 16
    assert switch_ports_needed(5) == 7 and choose_switch(5) == 8
    with pytest.raises(ValueError):
        choose_switch(40)
    assert panels_needed(24) == 1 and panels_needed(25) == 2 and panels_needed(40) == 2
    assert rack_units(RACK_LAYOUT) == 6 and choose_rack(6) == 9  # 7,5 → 9 U
    assert choose_rack(10) == 15 and choose_rack(8) == 12
    assert boxes_needed([93, 83, 66, 60, 47, 38]) == 2 and boxes_needed([150, 150]) == 1
    assert boxes_needed([160, 160]) == 2  # 320 m mais aucun raboutage : deux boîtes
    with pytest.raises(ValueError):
        boxes_needed([306])
    with pytest.raises(ValueError):
        rack_svg((RackItem("trop", 10),), 9)


def test_poe_budget_and_quote():
    assert poe_budget_w([4]) == 30 and poe_budget_w([3, 3]) == 30.8 and poe_budget_w([2]) == 7
    assert poe_budget_w([4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2]) == 133.6
    assert poe_verdict([4, 4, 3, 3, 3, 3], 120) == POE_KO and poe_verdict([4, 4], 60) == POE_OK
    lines = (QuoteLine("A", "a", 3, 10.0), QuoteLine("B", "b", 2, 4.55))
    assert quote_totals(lines) == (39.1, 8.21, 47.31)
    ht, vat, ttc = PLAN_QUOTE_TOTALS
    assert ht == round(sum(line.quantity * line.unit_price for line in PLAN_QUOTE), 2)
    assert vat == round(ht * 0.21, 2) and ttc == round(ht + vat, 2)
    ks = next(line for line in PLAN_QUOTE if line.ref == "KS")
    assert ks.quantity == 2 * len(PLAN.outlets)
    assert euro(1746.03) == "1 746,03 €" and euro(4.9) == "4,90 €" and euro(1234567.5) == "1 234 567,50 €"


def test_labels_recette_and_validation_order():
    assert label_for(1, 1, 7) == "B1-P1-07" and PATCH_ROWS[6][0] == "B1-P1-07" and PATCH_ROWS[6][2] == 7
    assert min_separation_mm("b") == 100 and min_separation_mm(None) == 300 and min_separation_mm("c") == 50
    assert link_verdict(LinkTest("x", True, 90, "PASS")) == T_OK
    assert link_verdict(LinkTest("x", True, 91, "PASS")) == T_LENGTH
    assert link_verdict(LinkTest("x", False, 20, "FAIL")) == T_WIRING
    assert link_verdict(LinkTest("x", True, 40, "FAIL")) == T_PERF
    with pytest.raises(ValueError):
        link_verdict(LinkTest("x", True, 40, "?"))
    assert validation_diagnosis(dict.fromkeys(("lien", "adresse", "passerelle", "poste", "internet", "partage"), True)) == D_OK
    expected = {"lien": D_PHYS, "adresse": D_IP, "passerelle": D_GW, "poste": D_PEER, "internet": D_NET, "partage": D_SHARE}
    for key, diagnosis in expected.items():
        assert validation_diagnosis(first_failure(key)) == diagnosis
    # un échec plus loin ne masque pas le premier
    results = first_failure("partage") | {"adresse": False}
    assert validation_diagnosis(results) == D_IP


def test_procedures_order():
    assert [t for t, _s in PROCEDURES] == [
        "Installer un mini-réseau, de l'étude à la réception",
        "Tester et certifier le câblage",
        "Valider le réseau dans l'ordre",
    ]
    install = [label for label, _d in INSTALL_STEPS]
    assert install[0] == "Analyser le besoin" and install[-1] == "Documenter et réceptionner"
    assert install.index("Chiffrer") < install.index("Poser") < install.index("Raccorder") < install.index("Tester")
    tests = [label for label, _d in TEST_STEPS]
    assert tests.index("Lire le câblage") < tests.index("Lire la longueur") < tests.index("Certifier")
    checks = [label for label, _d in CHECK_STEPS]
    assert checks == ["Lien", "Adresse", "Passerelle", "Autre poste", "Internet", "Partage", "Consigner"]


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    all_figures = PR18_FIGURES + tuple(f for f, _p in STATIC_FIGURES)
    keys = [f.key for f in all_figures]
    assert len(keys) == len(set(keys)) == 13 and len(PR18_FIGURES) >= 4  # ticket : ≥ 4 schémas
    for figure in all_figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR18_FIGURES}
    svg = by_key["pr18-plan-locaux"].svg
    points = re.findall(r'data-point="(\w+)"', svg)
    assert points == ["BAIE", "BOX"] + [o.key for o in PLAN.outlets]
    assert 'data-poe="4"' in svg and {r.name for r in PLAN.rooms} == set(re.findall(r'data-room="([^"]+)"', svg)) - set()
    rack = re.findall(r'data-item="([^"]+)" data-u="(\d)"', by_key["pr18-baie"].svg)
    assert [(escape(i.name), str(i.units)) for i in RACK_LAYOUT] == rack
    patch = re.findall(r'data-row="(\d+)" data-label="([^"]*)"', by_key["pr18-plan-brassage"].svg)
    assert patch == [(str(i), label_for(1, 1, i)) for i in range(1, 9)]
    poe = by_key["pr18-budget-poe"].svg
    assert 'data-total="133,6"' in poe
    assert re.findall(r'data-switch="([^"]+)" data-budget="(\d+)" data-verdict="([^"]+)"', poe) == [
        ("Switch A", "65", escape(POE_KO)), ("Switch B", "130", escape(POE_KO)), ("Switch C", "370", escape(POE_OK))]
    star = by_key["pr18-etoile"].svg
    assert re.findall(r'data-link="(\w+)"', star) == ["postes", "imprimante", "ecran", "ap"]
    for key, steps in (("pr18-procedure-installation", INSTALL_STEPS), ("pr18-procedure-tests", TEST_STEPS),
                       ("pr18-procedure-validation", CHECK_STEPS)):
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in by_key[key].svg, (key, label)


def test_schemas_to_complete_hide_their_answers():
    schemas = {f.key: f for f, _p in STATIC_FIGURES}
    plan_svg = schemas["pr18-plan-a-completer"].svg
    assert "data-point" not in plan_svg and re.findall(r'data-marker="(.)"', plan_svg) == [n for n, *_r in PLAN_BLANKS]
    rack_svg_text = schemas["pr18-baie-a-completer"].svg
    for number in "①②③④":
        assert f"{number} ?" in rack_svg_text
    assert rack_svg_text.count("Switch") == 0 and rack_svg_text.count("Bandeau") == 0
    chain = schemas["pr18-lien-a-completer"].svg
    assert "cordon" not in chain.lower() and "Panneau" not in chain and "Prise murale" not in chain and "lien permanent" not in chain.lower()
    star = schemas["pr18-etoile-a-completer"].svg
    assert ">Box" not in star and 'data-node="box"' not in star and "switch (" not in star.lower() and 'data-link="ap"' not in star and "Switch (centre" not in star and "fibre" not in star.lower() and "Point d'accès" not in star
    patch = schemas["pr18-brassage-a-completer"].svg
    assert "B1-P1-03" not in patch and "B1-P1-06" not in patch and "B1-P1-07" not in patch and "B1-P1-08" in patch


def test_static_figure_files_are_the_generated_svg():
    assert len(STATIC_FIGURES) == 5
    for figure, path in STATIC_FIGURES:
        content = (STATIC_DIR / path).read_text()
        assert content == static_svg(figure)
        assert content.startswith("<svg ") and "xmlns=" in content and "<title>" in content


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 18 and len(EXAM_ITEMS) == 10  # ticket : ≥ 18 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_SCHEMA) >= 5 and kinds.count(KIND_QUOTE) >= 4  # ticket : ≥ 5 schémas, ≥ 4 devis
    for kind in (KIND_ORDER, KIND_PLAN, KIND_TEST, KIND_SAFETY):
        assert kind in kinds
    schema_images = {d.image for i in PRACTICE_ITEMS if i.kind == KIND_SCHEMA for d in i.documents}
    assert schema_images == {p for _f, p in STATIC_FIGURES}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert covered == REQ == set(plan.COURSE_SLOTS_BY_CODE["PR18"].requirement_ids)
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 4


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i].split(" — ")[0] for i in o.correct]

    assert ordered("E01") == [label for label, _d in INSTALL_STEPS]
    assert ordered("E02") == [label for label, _d in CHECK_STEPS]
    assert ordered("E03") == [label for label, _d in TEST_STEPS]

    def answers(key: str) -> dict[str, str]:
        c = by_key[key].classification
        return dict(zip(c.elements, (c.categories[i] for i in c.correct), strict=True))

    def find(mapping: dict[str, str], fragment: str) -> str:
        return next(v for k, v in mapping.items() if fragment in k)

    e04 = answers("E04")
    assert find(e04, "ligne de l'opérateur") == PLACE_BOX and find(e04, "fermé à clé") == PLACE_RACK
    assert find(e04, "open space") == PLACE_AP and find(e04, "plinthes") == PLACE_PATH and find(e04, "imprimante") == PLACE_OUTLET
    e05 = answers("E05")
    assert find(e05, "140 m") == "Fibre optique" and find(e05, "presse") == "Fibre optique"
    assert find(e05, "Caméra analogique") == "Coaxial 75 Ω" and find(e05, "télévision") == "Coaxial 75 Ω"
    assert find(e05, "atelier") == "F/UTP" and find(e05, "néons") == "U/UTP" and find(e05, "35 m") == "U/UTP"
    e06 = answers("E06")
    assert find(e06, "B1-P1-01") == T_OK and find(e06, "B1-P1-02") == T_WIRING and find(e06, "B1-P1-05") == T_WIRING
    assert find(e06, "B1-P1-03") == T_LENGTH and find(e06, "B1-P1-07") == T_LENGTH and find(e06, "B1-P1-04") == T_PERF
    e07 = answers("E07")
    assert find(e07, "169.254") == D_IP and find(e07, "Accès refusé") == D_SHARE and find(e07, "brassée sur aucun") == D_PHYS
    assert find(e07, "aucun site") == D_NET and find(e07, "ce poste est éteint") == D_PEER and find(e07, "192.168.1.1 échoue") == D_GW
    for item in PRACTICE_ITEMS:
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key
        if item.classification:
            correct = list(item.classification.correct)
            assert correct[: len(item.classification.categories)] != list(range(len(item.classification.categories))), item.key
            assert len(set(correct)) == len(item.classification.categories), item.key


def test_numbers_in_corrections_match_calculations():
    by_key = {i.key: i for i in PRACTICE_ITEMS + EXAM_ITEMS}

    def text(key: str) -> str:
        item = by_key[key]
        return " ".join((*item.correction, *(c.expected for c in item.criteria)))

    assert E13_LENGTHS == (15, 19, 11, 27) and E13_TOTAL_M == 106 and E13_BOXES == 1
    assert "106 m" in text("E13") and "12 keystones" in text("E13") and "16 ports" in text("E13")
    assert (E14_HT, E14_VAT, E14_TTC) == PLAN_QUOTE_TOTALS
    assert euro(E14_TTC) in text("E14") and "26" in text("E14") and "21 %" in text("E14")
    assert E15_PORTS == 18 and E15_POE == 88.8 and E15_CHOICE == "S2" and "88,8 W" in text("E15")
    assert E16_USED == 10 and E16_RACK == 15 and "15 U" in text("E16")
    assert E17_LENGTHS == (47, 66, 83, 93, 38, 60) and E17_TOTAL == 387 and E17_BOXES == 2
    assert "93 m" in text("E17") and "387 m" in text("E17") and "2 boîtes" in text("E17")
    assert "100 mm" in text("E18") and "300 mm" in text("E18")
    assert "91 m" in text("E10") and "23 m" in text("E08")
    assert X01_LENGTHS == (93, 51) and "93 m" in text("X01")
    assert X03_LINKS == 14 and X03_SWITCH == 24 and "28 keystones" in text("X03")
    assert (X04_HT, X04_VAT, X04_TTC) == (469.4, 98.57, 567.97) and euro(X04_TTC) in text("X04")
    assert X05_TOTAL == 121.6 and "121,6 W" in text("X05")
    assert "port 5 du switch 2" in text("X09") and "3 U libres" in text("X10")


def test_schema_documents_point_to_static_files():
    item = next(i for i in PRACTICE_ITEMS if i.key == "E08")
    layout = _document_layout(item.documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr18-plan-a-completer.svg"
    assert "local technique" in layout["alt"] and "non officiel" in layout["notice"]


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("étoile", "90 m", "100 m", "305 m", "keystone", "panneau de brassage", "passe-câbles",
                  "b1-p1-07", "même repère", "21 %", "15,4 w", "30 w", "budget", "angle droit", "300 mm",
                  "fibre", "coaxial 75 ω", "169.254", "passerelle", "pass", "fail", "procès-verbal", "dhcp"):
        assert right in text, right
    for wrong in ("le câble traverse en diagonale", "un keystone par lien suffit", "tva de 6 %", "cuivre entre deux bâtiments convient",
                  "lien permanent de 100 m", "budget poe illimité", "t568a d'un côté et t568b de l'autre pour un lien droit"):
        assert wrong not in text, wrong


def test_no_acronym_question_and_full_context():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.title, item.context, *item.instructions))
        assert not re.search(r"que signifie|que veut dire|développe[rz]? l'acronyme", text, re.IGNORECASE), item.key
        assert len(item.context) >= 150, item.key
        assert "officiel" not in item.title.lower(), item.key


def test_items_content_matches_existing_question_types():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        content = item_content(item, list(range(1, len(item.documents) + 1)))
        validate_content(item.question_type, 1, content)


# =============================================================================================
# 4. Cours
# =============================================================================================


def test_five_resolved_cases_procedures_and_exam_not_in_course():
    text = _text(_course_raw())
    assert [title for title, *_r in CASES] == [
        "Cas 1 — Cabinet comptable : plan, baie et devis", "Cas 2 — Salle de classe de 12 PC",
        "Cas 3 — Bureaux et atelier : perturbations et courant fort",
        "Cas 4 — Agence : Wi-Fi, caméras et téléphones en PoE", "Cas 5 — Deux bâtiments : liaison, recette et validation"]
    for title, *_r in CASES:
        assert escape(title) in _course_raw() or title in text, title
    assert text.count("Conclusion rédigée.") == 5
    assert "133,6 W" in text and "F/UTP" in text and "300 mm" in text
    for i in (1, 2, 3):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key
    # chaque schéma à compléter est dessiné dans sa carte d'exercice
    for figure, _path in STATIC_FIGURES:
        assert f'id="fig-{figure.key}"' in course, figure.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr18_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "besoin", "plan des locaux", "topologie en étoile", "switch", "point d'accès", "box", "routeur",
        "prises", "baie", "cuivre", "fibre", "coaxial", "longueur", "cheminement", "repérage", "sécurité",
        "courant fort", "plan de câblage", "nomenclature", "panneau de brassage", "keystone", "continuité",
        "certification", "poe", "configuration de base", "autre poste", "internet", "partage",
        "documentation", "recette", "devis",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-36", "AP-38"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "convention du cours" in text.lower()
    for link in ("/uaa/ampcr-mc14", "/uaa/ampcr-mc15", "/uaa/ampcr-pratique-pr13", "/uaa/ampcr-pratique-pr15",
                 "/uaa/ampcr-pratique-pr17", "/uaa/ampcr-pratique-pr20", "/uaa/ampcr-pratique-pr24",
                 f"/uaa/{PR18_SLUG}/practice", f"/uaa/{PR18_SLUG}/exam"):
        assert link in raw, link
    for unpublished in ("/uaa/ampcr-pratique-pr19", "/uaa/ampcr-pratique-pr21", "/uaa/ampcr-pratique-pr23"):
        assert unpublished not in raw, unpublished
    anchors = set(re.findall(r'id="(pr18-e\d\d)"', raw))
    assert anchors == {f"pr18-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr18-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr18_course_sections()]
    assert kinds[:12] == ["theory"] * 12
    assert kinds[12:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR18"]
    assert slot.ticket == 219 and slot.title == PR18_TITLE == PRACTICAL_COURSES_BY_CODE["PR18"].title


def test_seed_publishes_pr18_in_practical_module_idempotently(db_session):
    module, uaa = _pr18(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR18_TITLE and uaa.position == 18
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR18").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr18_course_sections())
    assert {"PR17", "PR18"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR17") < ordered.index("EX03") < ordered.index("PR18") < ordered.index("PR20")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr18(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr18_specific():
    context = _pedagogical_context_for("PR18")
    assert context is get_practical_context("PR18")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("topologie en étoile", "lien permanent ≤ 90 m", "boîtes de 305 m", "classe a 300 mm",
                   "2 par lien", "+ 1 port pour la box", "TVA belge 21 %", "PASS/FAIL", "169.254"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "un seul keystone par lien" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr18(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR18_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200


def test_practical_home_and_matrix_show_pr18(client, db_session):
    _pr18(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR19 (#220) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR18"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == audit_proven_ids()  # « validé » : preuves de l'audit #235
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr18(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR18"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr18(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR18", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr18(db_session)
    for _ in range(2):  # 20 exercices : deux sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

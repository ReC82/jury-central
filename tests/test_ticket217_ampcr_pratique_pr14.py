"""Ticket #217 — AMPCR pratique écrite, PR14 « Débits, distances, atténuation et impédance ».

Couvre : données de référence et calculs **recontrôlés ici** indépendamment (unités, préfixes,
durée d'une copie, rendement TCP, normes Ethernet et longueurs, décibels, ACR, réflexions,
bilan optique et portées, auto-négociation et duplex) ; schémas SVG (validité, accessibilité,
données dessinées) ; exercices et mini-examen (format du socle, remises en ordre et classements
auto-corrigés, nombres des corrigés, pas de question d'acronyme) ; cours (matière du ticket,
3 procédures, 5 cas résolus, affirmations techniques justes, supports fictifs, cartes) ; banque,
seed, pages et sessions. Aucun appel IA réel : `FakeAIProvider` partout."""

import math
import re
from html import escape

import pytest

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    get_practical_context,
    import_practical_bank,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_pr14_bank import (
    E09_T_FAST,
    E09_T_GIGA,
    E10_MEASURED_MBPS,
    E12_ACR_02,
    E12_FAULTS,
    E13_LINK,
    E14_THICK_LOSS,
    E14_THIN_LOSS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_DISTANCE,
    KIND_FIBRE,
    KIND_LINK,
    KIND_ORDER,
    KIND_RATE,
    KIND_SIGNAL,
    PRACTICE_ITEMS,
    REQ,
    X01_T,
    X05_OUT_MW,
    X06_LINK,
    X09_GAMMA,
    validate_items,
)
from app.v1.ampcr_pratique_pr14_course import CASES, PR14_SLUG, PR14_TITLE, pr14_course_sections
from app.v1.ampcr_pratique_pr14_figures import (
    BUDGET_EXAMPLE,
    COAX_SEGMENT_MAX_DB,
    DB_EXAMPLES,
    F_BUDGET,
    F_REACH,
    FIBRE_STEPS,
    FULL,
    HALF,
    LINK_STEPS,
    M_10G_COPPER,
    M_10G_LR,
    M_10G_OM3,
    M_10G_OM4,
    N_DOWN,
    N_FAST,
    N_GIGA,
    N_MISMATCH,
    PR14_FIGURES,
    PROCEDURES,
    R_MATCHED,
    R_OPEN,
    R_PARTIAL,
    R_SHORT,
    REACH_BARS,
    REACH_M,
    REFLECTION_EXAMPLES,
    TCP_EFFICIENCY,
    TRANSFER_STEPS,
    V_CATEGORY,
    V_CONDITIONAL,
    V_LENGTH,
    V_OK,
    FibreLink,
    Port,
    acr_db,
    cable_loss_db,
    choose_10g,
    copper_verdict,
    dbm,
    duration_fr,
    fibre_errors,
    fibre_loss_db,
    fr,
    fraction_after,
    link_result,
    loss_db,
    mw,
    negotiate,
    rate_bps,
    reflected_power_pct,
    reflection_coefficient,
    return_loss_db,
    to_bits,
    transfer_time_s,
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

SLUG = "ampcr-pratique-pr14"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr14_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr14(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR14")
    return module, uaa


# =============================================================================================
# 1. Données de référence et calculs, recontrôlés indépendamment
# =============================================================================================


def test_units_and_transfer_time():
    assert to_bits(1, "o") == 8 and to_bits(1, "ko") == 8000 and to_bits(1, "Kio") == 8192
    assert to_bits(18, "Go") == 144e9 and to_bits(1, "Gio") == 8 * 1_073_741_824
    assert rate_bps(1, "Gb/s") == 1e9 and rate_bps(100, "Mb/s") == 1e8
    with pytest.raises(ValueError):
        to_bits(1, "Gx")
    with pytest.raises(ValueError):
        rate_bps(1, "Mo/s")  # un débit s'écrit en bits par seconde
    assert transfer_time_s(144e9, 1e9, 0.9) == pytest.approx(160)
    assert duration_fr(160) == "2 min 40 s" and duration_fr(4255.3) == "1 h 10 min 55 s" and duration_fr(7) == "7 s"
    # Rendement TCP/IPv4 sur Ethernet : 1460 / (8 + 14 + 1500 + 4 + 12).
    assert TCP_EFFICIENCY == pytest.approx(1460 / 1538) and 0.949 < TCP_EFFICIENCY < 0.95
    assert E09_T_FAST == pytest.approx(1600) and E09_T_GIGA == pytest.approx(160)
    assert E10_MEASURED_MBPS == pytest.approx(4.5 * 2**30 * 8 / 450 / 1e6)
    assert X01_T == pytest.approx(2.4e9 * 8 / 90e6)
    assert fr(120, 0) == "120" and fr(2.27, 2) == "2,27"


def test_copper_and_coax_rules():
    assert copper_verdict("1000BASE-T", "Cat5e", 100) == V_OK
    assert copper_verdict("1000BASE-T", "Cat6A", 101) == V_LENGTH  # 100 m pour toutes les catégories
    assert copper_verdict("10GBASE-T", "Cat6A", 100) == V_OK
    assert copper_verdict("10GBASE-T", "Cat6", 55) == V_CONDITIONAL
    assert copper_verdict("10GBASE-T", "Cat6", 56) == V_CATEGORY
    assert copper_verdict("10GBASE-T", "Cat5e", 20) == V_CATEGORY
    assert copper_verdict("100BASE-TX", "Cat5", 100) == V_OK
    assert copper_verdict("10BASE-T", "Cat3", 100) == V_OK
    assert copper_verdict("1000BASE-T", "Cat3", 10) == V_CATEGORY
    # IEEE 802.3 : 8,5 dB à 10 MHz par segment ; 185 m et 500 m.
    assert COAX_SEGMENT_MAX_DB == 8.5
    assert E14_THIN_LOSS == pytest.approx(9.66) and E14_THIN_LOSS > 8.5
    assert E14_THICK_LOSS == pytest.approx(8.16) and E14_THICK_LOSS <= 8.5


def test_decibels_and_crosstalk():
    assert loss_db(2, 1) == pytest.approx(3.0103, abs=1e-3)
    assert loss_db(100, 1) == pytest.approx(20)
    assert fraction_after(10) == pytest.approx(0.1) and fraction_after(3) == pytest.approx(0.501, abs=1e-3)
    assert dbm(1) == 0 and dbm(20) == pytest.approx(13.01, abs=0.01) and mw(-20) == pytest.approx(0.01)
    assert cable_loss_db(60, 19.8) == pytest.approx(11.88)
    assert X05_OUT_MW == pytest.approx(1.0, abs=0.01)
    assert acr_db(37.2, 28.4) == pytest.approx(8.8) == E12_ACR_02
    assert E12_FAULTS == {"B1-P1-01": [], "B1-P1-02": [], "B1-P1-03": ["NEXT"],
                          "B1-P1-04": ["longueur", "affaiblissement"]}


def test_reflections():
    assert reflection_coefficient(50, 50) == 0
    assert reflection_coefficient(None, 50) == 1 and reflection_coefficient(0, 50) == -1
    assert reflection_coefficient(75, 50) == pytest.approx(0.2) == X09_GAMMA
    assert reflection_coefficient(50, 75) == pytest.approx(-0.2)
    assert reflected_power_pct(0.2) == pytest.approx(4)
    assert return_loss_db(0.2) == pytest.approx(13.98, abs=0.01) and return_loss_db(0) is None
    assert return_loss_db(1) == 0


def test_fibre_budget_and_reach():
    assert fibre_loss_db(220, 3.5, 2, 0) == pytest.approx(2.27)
    assert BUDGET_EXAMPLE.loss_db == pytest.approx(2.27) and BUDGET_EXAMPLE.margin_db == pytest.approx(0.33)
    assert E13_LINK.loss_db == pytest.approx(4.8) and E13_LINK.margin_db == pytest.approx(1.4)
    assert X06_LINK.loss_db == pytest.approx(3.5) and X06_LINK.margin_db == pytest.approx(2.7)
    # IEEE 802.3 : portée selon module ET fibre.
    assert REACH_M[("10GBASE-SR", "OM3")] == 300 and REACH_M[("10GBASE-SR", "OM4")] == 400
    assert REACH_M[("10GBASE-SR", "OM1")] == 33 and REACH_M[("1000BASE-SX", "OM2")] == 550
    assert REACH_M[("10GBASE-LR", "OS2")] == 10000 and REACH_M[("1000BASE-LX", "OS2")] == 5000
    too_long = FibreLink("x", "10GBASE-SR", "OM3", 850, 450, 2, 0, 2.6)
    assert fibre_errors(too_long) == [F_REACH, F_BUDGET]  # 0,45 × 3,5 + 1,5 = 3,08 dB > 2,6
    assert fibre_errors(FibreLink("x", "10GBASE-SR", "OM3", 850, 320, 0, 0, 2.6)) == [F_REACH]
    assert choose_10g(100) == M_10G_COPPER and choose_10g(90, between_buildings=True) == M_10G_OM3
    assert choose_10g(300) == M_10G_OM3 and choose_10g(301) == M_10G_OM4 and choose_10g(401) == M_10G_LR
    with pytest.raises(ValueError):
        choose_10g(12000)


def test_negotiation_and_duplex():
    auto, forced_full = Port(), Port(auto=False, speed=100, duplex=FULL)
    assert link_result(negotiate(auto, auto)) == N_GIGA
    assert link_result(negotiate(auto, auto, four_pairs_ok=False)) == N_FAST  # rétrogradation
    link = negotiate(auto, forced_full)
    assert link.speed == 100 and (link.duplex_a, link.duplex_b) == (HALF, FULL) and link.mismatch
    assert link_result(link) == N_MISMATCH
    assert link_result(negotiate(forced_full, forced_full)) == N_FAST
    assert link_result(negotiate(auto, Port(max_speed=100))) == N_FAST
    assert link_result(negotiate(Port(auto=False, speed=10, duplex=HALF), forced_full)) == N_DOWN
    assert not negotiate(auto, Port(auto=False, speed=100, duplex=HALF)).mismatch  # half des deux côtés
    with pytest.raises(ValueError):
        Port(auto=False, speed=1000, duplex=FULL)  # 1000BASE-T exige l'auto-négociation


def test_procedures_order():
    assert [label for label, _d in TRANSFER_STEPS] == ["Taille en bits", "Débit en b/s", "Débit utile", "Diviser", "Convertir", "Vérifier"]
    assert LINK_STEPS[0][0] == "Relever" and LINK_STEPS[3][0] == "Câble"
    assert FIBRE_STEPS[2][0] == "Calculer la perte"
    assert len(PROCEDURES) == 3


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR14_FIGURES]
    assert len(keys) == len(set(keys)) == 9  # ticket : au moins 4 schémas ou documents
    for figure in PR14_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR14_FIGURES}
    assert by_key["pr14-octet-prefixes"].svg.count("data-bit=") == 8
    bars = re.findall(r'data-standard="([^"]+)" data-m="(\d+)"', by_key["pr14-portees"].svg)
    assert [(escape(n), m) for n, m in ((n, int(m)) for n, m in bars)] == [(escape(n), m) for n, _md, m in REACH_BARS]
    assert ("10BASE2", 185) in [(n, int(m)) for n, m in bars] and ("10BASE5", 500) in [(n, int(m)) for n, m in bars]
    db_bars = re.findall(r'data-db="([\d,]+)" data-percent="([\d,]+)"', by_key["pr14-decibels"].svg)
    assert [d for d, _p in db_bars] == [fr(d) for d in DB_EXAMPLES]
    assert dict(db_bars)["10"] == "10" and dict(db_bars)["3"] == "50,1"
    gammas = re.findall(r'data-gamma="(-?[\d,]+)"', by_key["pr14-reflexions"].svg)
    assert gammas == [fr(reflection_coefficient(z, line), 2) for _l, line, z in REFLECTION_EXAMPLES]
    assert "puissance réfléchie : 100 %" in by_key["pr14-reflexions"].svg  # pas de « 1 % » tronqué
    budget = by_key["pr14-bilan-optique"].svg
    parts = dict(re.findall(r'data-part="(\w+)" data-db="([\d,]+)"', budget))
    assert parts == {"fibre": "0,77", "connecteurs": "1,5", "epissures": "0", "marge": "0,33"}
    assert 'data-crosstalk="next"' in by_key["pr14-diaphonie"].svg and 'data-crosstalk="fext"' in by_key["pr14-diaphonie"].svg
    for key, steps in (("pr14-procedure-duree", TRANSFER_STEPS), ("pr14-procedure-liaison", LINK_STEPS),
                       ("pr14-procedure-bilan", FIBRE_STEPS)):
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in by_key[key].svg, (key, label)


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 18 and len(EXAM_ITEMS) == 10  # ticket : ≥ 18 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 3), (KIND_RATE, 3), (KIND_DISTANCE, 3), (KIND_SIGNAL, 3),
                          (KIND_FIBRE, 2), (KIND_LINK, 3)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered and "AP-21" in covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR14"].requirement_ids) == REQ
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 5
    assert sum(1 for i in PRACTICE_ITEMS if i.documents) >= 6
    # Ticket : exercices chiffrés avec unités, à l'entraînement et à l'examen.
    exam_text = " ".join(" ".join(i.correction) for i in EXAM_ITEMS)
    for unit in ("Mb/s", "Mo/s", "dB", "mW", "km", " s"):
        assert unit in exam_text, unit


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i].split(" — ")[0] for i in o.correct]

    assert ordered("E01") == [label for label, _d in TRANSFER_STEPS]
    assert ordered("E02") == [label for label, _d in LINK_STEPS]
    assert ordered("E03") == [label for label, _d in FIBRE_STEPS]

    def answers(key: str) -> dict[str, str]:
        c = by_key[key].classification
        return dict(zip(c.elements, (c.categories[i] for i in c.correct), strict=True))

    def find(mapping: dict[str, str], fragment: str) -> str:
        return next(v for k, v in mapping.items() if fragment in k)

    e04 = answers("E04")
    assert find(e04, "Cat6, canal de 45") == V_CONDITIONAL and find(e04, "Cat6, canal de 80") == V_CATEGORY
    assert find(e04, "120 m") == V_LENGTH and find(e04, "Cat3") == V_CATEGORY and find(e04, "Cat6A, canal de 95") == V_OK
    e05 = answers("E05")
    assert find(e05, "de 3 dB") == "La moitié" and find(e05, "de 6 dB") == "Le quart"
    assert find(e05, "Deux tronçons") == "Un centième" and find(e05, "3 dB puis") == "Un dixième"
    assert find(e05, "30 dB") == "Un millième"
    e06 = answers("E06")
    assert find(e06, "paire 7-8 coupée") == N_FAST and find(e06, "port du switch forcé à 100 Mb/s full") == N_MISMATCH
    assert find(e06, "10 Mb/s half") == N_DOWN and find(e06, "testé conforme") == N_GIGA
    assert find(e06, "switch forcé à 100 Mb/s half") == N_MISMATCH
    e07 = answers("E07")
    assert find(e07, "même salle") == M_10G_COPPER and find(e07, "bâtiment B") == M_10G_OM3
    assert find(e07, "360 m") == M_10G_OM4 and find(e07, "8 km") == M_10G_LR
    e08 = answers("E08")
    assert find(e08, "fermé par un terminateur 50 Ω") == R_MATCHED and find(e08, "retiré") == R_OPEN
    assert find(e08, "âme touche") == R_SHORT and find(e08, "IBM") == R_PARTIAL
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu, aucun classement trivial
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key
        if item.classification:
            assert list(item.classification.correct) != list(range(len(item.classification.elements))), item.key
            assert len(set(item.classification.correct)) > 1, item.key


def test_numbers_in_corrections_match_calculations():
    by_key = {i.key: i for i in PRACTICE_ITEMS + EXAM_ITEMS}
    text = lambda key: " ".join(by_key[key].correction)
    assert "1600 s" in text("E09") and "26 min 40 s" in text("E09") and "2 min 40 s" in text("E09")
    assert "85,9 Mb/s" in text("E10") and "80 Mb/s" in text("E10")
    assert "4,8 dB" in text("E13") and "1,4 dB" in text("E13")
    assert "9,66 dB" in text("E14") and "8,16 dB" in text("E14")
    assert "125 Mo/s" in text("E15")
    assert "3 min 33 s" in text("X01") and "62,5 Mo/s" in text("X02") and "1 mW" in text("X05")
    assert "3,5 dB" in text("X06") and "2,7 dB" in text("X06") and "0,2" in text("X09") and "4 %" in text("X09")
    assert math.isclose(X09_GAMMA, 0.2)


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("8 bits", "125 mo/s", "préfixes décimaux", "2³⁰", "débit utile", "débit nominal", "1460",
                  "100 m", "90 m", "cat5e", "cat6a", "55 m", "37 m", "4 paires", "1-2 et 3-6", "10base2",
                  "185 m", "10base5", "500 m", "8,5 db", "10 × log10", "3 db", "0 dbm = 1 mw", "next", "fext",
                  "plus la valeur en db est grande", "acr", "100 ω", "50 ω", "75 ω", "γ = (zcharge − zligne)",
                  "monomode", "multimode", "3,5 db/km", "0,4 db/km", "0,75 db", "0,3 db", "300 m sur om3",
                  "half duplex", "full duplex", "csma/cd", "auto-négociation", "désaccord de duplex",
                  "rétrograde", "ethtool"):
        assert right in text, right
    for wrong in ("1 gb/s = 1 go/s", "plus le next est petit, mieux c'est", "un meilleur câble permet 150 m",
                  "cat6 tient 10 gb/s sur 100 m", "6 db font perdre 6 %", "mélanger 50 et 75 ω est sans effet",
                  "le hub évite les collisions", "100base-tx utilise les 4 paires", "forcer un seul côté corrige"):
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
    assert len(CASES) == 5
    for title, _s, _steps, conclusion in CASES:
        assert title in text and escape(conclusion) in _course_raw() or conclusion in text, title
    assert text.count("Conclusion rédigée.") == 5
    assert "7 min 6 s" in text and "1 h 10 min 55 s" in text and "6,5 %" in text and "0,33 dB" in text
    for i in (1, 2, 3):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr14_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "bit", "octet", "b/s", "multiples", "décimaux", "durée", "débit utile", "nominal",
        "10 mb/s", "100 mb/s", "1 gb/s", "10 gb/s", "100 m", "90 m", "cordons", "cat5e", "cat6a", "cat6",
        "distance conditionnelle", "10base2", "185 m", "10base5", "500 m",
        "atténuation", "db", "bruit", "diaphonie", "next", "blindage", "réflexions", "impédance", "50 ω", "75 ω",
        "monomode", "multimode", "pertes", "portée", "module optique",
        "duplex", "négociation", "collisions", "100 mb/s au lieu de 1 gb/s",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-19", "AP-20", "AP-21"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "convention du cours" in text.lower()
    for link in ("/uaa/ampcr-mc15", "/uaa/ampcr-pratique-pr13", "/uaa/ampcr-pratique-pr15",
                 "/uaa/ampcr-pratique-pr16", f"/uaa/{PR14_SLUG}/practice", f"/uaa/{PR14_SLUG}/exam"):
        assert link in raw, link
    # PR17 n'est pas encore publié : renvoi en texte seulement.
    assert "/uaa/ampcr-pratique-pr17" not in raw and "PR17" in raw
    anchors = set(re.findall(r'id="(pr14-e\d\d)"', raw))
    assert anchors == {f"pr14-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr14-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr14_course_sections()]
    assert kinds[:10] == ["theory"] * 10
    assert kinds[10:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR14"]
    assert slot.ticket == 217 and slot.title == PR14_TITLE == PRACTICAL_COURSES_BY_CODE["PR14"].title


def test_seed_publishes_pr14_in_practical_module_idempotently(db_session):
    module, uaa = _pr14(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR14_TITLE and uaa.position == 14
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR14").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr14_course_sections())
    assert {"PR13", "PR14", "PR15", "PR16"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR13") < ordered.index("PR14") < ordered.index("PR15")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr14(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr14_specific():
    context = _pedagogical_context_for("PR14")
    assert context is get_practical_context("PR14")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("1 Gb/s ÷ 8 = 125 Mo/s", "94,9 %", "Cat6 55 m", "185 m", "8,5 dB", "3 dB ≈ ÷ 2", "ACR",
                   "Γ = (Zcharge − Zligne)", "0,75 dB", "300 m OM3", "half duplex", "paire 4-5 / 7-8"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "bits/octets" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr14(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR14_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and "jc-pr-console" in html


def test_practical_home_and_matrix_show_pr14(client, db_session):
    _pr14(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"18 cours publiés sur 30 prévus", _text(home))
    for req in REQ:
        assert plan.requirement_status(req, {"PR14"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr14(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR14"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr14(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR14", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr14(db_session)
    for _ in range(2):  # 19 exercices : deux sessions de 10 couvrent presque toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

"""Ticket #218 — AMPCR pratique écrite, PR17 « Fibre optique — choix, raccordement et
diagnostic ».

Couvre : données de référence et calculs **recontrôlés ici** indépendamment (géométrie et types
de fibre, connecteurs et polissage, compatibilité module / fibre / portée, polarité, puissance
reçue et plage de la fiche, photométrie, OTDR : distance, nature des événements, cassure ;
rayon de courbure) ; schémas SVG (validité, accessibilité, données dessinées) ; exercices et
mini-examen (format du socle, remises en ordre et classements auto-corrigés, nombres des
corrigés, pas de question d'acronyme) ; cours (matière du ticket, 3 procédures, 5 cas résolus,
affirmations techniques justes, supports fictifs, cartes) ; banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr17_bank import (
    CAUSE_BREAK,
    CAUSE_DIRTY,
    CAUSE_MODULE,
    CAUSE_POLARITY,
    CAUSE_REACH,
    E09_LOSSES,
    E09_MAX,
    E10_BREAK,
    E11_LOSS_AB,
    E11_MAX,
    E12_LOSS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_CHOICE,
    KIND_CONNECT,
    KIND_DIAG,
    KIND_MEASURE,
    KIND_ORDER,
    KIND_SAFETY,
    PRACTICE_ITEMS,
    REQ,
    X05_BREAK,
    X06_LOSS,
    X06_MAX,
    X10_RX,
    X10_RX_AFTER,
    validate_items,
)
from app.v1.ampcr_pratique_pr17_course import CASES, PR17_SLUG, PR17_TITLE, pr17_course_sections
from app.v1.ampcr_pratique_pr17_figures import (
    C_FIBRE,
    C_OK,
    C_PAIR,
    C_REACH,
    CHAIN_ELEMENTS,
    CHAIN_TOTAL_DB,
    CLEAN_STEPS,
    DIAG_STEPS,
    FAM_LASER_MM,
    FAM_OLD_MM,
    FAM_SM,
    FIBRE_KINDS_BY_CODE,
    INSTALL_STEPS,
    LR_SPEC,
    O_BEND,
    O_CONNECTOR,
    O_END,
    O_SPLICE,
    OTDR_EXAMPLE,
    P_KO,
    P_OK,
    PR17_FIGURES,
    PROCEDURES,
    RX_HIGH,
    RX_LOW,
    RX_NONE,
    RX_OK,
    OtdrEvent,
    break_position_m,
    dbm_fr,
    fibre_family,
    fibre_mode,
    max_link_loss_db,
    measured_loss_db,
    min_bend_radius_mm,
    module_errors,
    module_verdict,
    otdr_distance_m,
    otdr_event_kind,
    photometry_verdict,
    polarity_ok,
    polish_compatible,
    rx_power_dbm,
    rx_status,
    trace_points,
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

SLUG = "ampcr-pratique-pr17"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr17_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr17(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR17")
    return module, uaa


# =============================================================================================
# 1. Données de référence et calculs, recontrôlés indépendamment
# =============================================================================================


def test_fibre_kinds_and_families():
    assert FIBRE_KINDS_BY_CODE["OM1"].core_um == 62.5 and FIBRE_KINDS_BY_CODE["OM3"].core_um == 50
    assert FIBRE_KINDS_BY_CODE["OS2"].core_um == 9 and FIBRE_KINDS_BY_CODE["OS2"].jacket == "jaune"
    assert "aqua" in FIBRE_KINDS_BY_CODE["OM3"].jacket and FIBRE_KINDS_BY_CODE["OM1"].jacket == "orange"
    assert FIBRE_KINDS_BY_CODE["OS2"].wavelengths == (1310, 1550) and 850 in FIBRE_KINDS_BY_CODE["OM4"].wavelengths
    assert fibre_mode("OM4") == "multimode" and fibre_mode("OS1") == "monomode"
    assert fibre_family("OM2") == FAM_OLD_MM and fibre_family("OM4") == FAM_LASER_MM and fibre_family("OS2") == FAM_SM
    with pytest.raises(ValueError):
        fibre_mode("CAT6")
    assert polish_compatible("APC", "APC") and not polish_compatible("APC", "UPC")


def test_module_compatibility_and_polarity():
    assert module_verdict("10GBASE-SR", "10GBASE-SR", "OM3", 300) == C_OK
    assert module_verdict("10GBASE-SR", "10GBASE-SR", "OM3", 301) == C_REACH
    assert module_verdict("10GBASE-SR", "10GBASE-SR", "OM4", 400) == C_OK
    assert module_verdict("10GBASE-SR", "10GBASE-SR", "OM2", 83) == C_REACH
    assert module_verdict("1000BASE-SX", "1000BASE-SX", "OM2", 550) == C_OK
    assert module_verdict("10GBASE-LR", "10GBASE-LR", "OS2", 10000) == C_OK
    assert module_verdict("10GBASE-LR", "10GBASE-LR", "OM4", 50) == C_FIBRE
    assert module_verdict("10GBASE-SR", "10GBASE-SR", "OS2", 10) == C_FIBRE
    assert module_errors("10GBASE-SR", "10GBASE-LR", "OS2", 2000) == [C_PAIR, C_FIBRE]
    with pytest.raises(ValueError):  # portée non tabulée : pas d'invention
        module_verdict("1000BASE-SX", "1000BASE-SX", "OM3", 100)
    assert polarity_ok("RX") and not polarity_ok("TX")
    with pytest.raises(ValueError):
        polarity_ok("A")


def test_losses_rx_power_and_photometry():
    # PR14 : 0,4 dB/km OS2, 3,5 dB/km multimode à 850 nm, 0,75 dB par connecteur, 0,3 par épissure
    assert math.isclose(max_link_loss_db(800, "OS2", 1310, 2, 2), 0.8 * 0.4 + 1.5 + 0.6)
    assert math.isclose(CHAIN_TOTAL_DB, 2.42) and math.isclose(sum(db for *_r, db in CHAIN_ELEMENTS), 2.42)
    assert math.isclose(max_link_loss_db(100, "OM3", 850, 2, 0), 1.85)
    assert rx_power_dbm(-2.1, 1.9) == -4.0
    assert measured_loss_db(-10.0, -12.3) == 2.3
    assert photometry_verdict(2.74, 2.74) == P_OK and photometry_verdict(2.75, 2.74) == P_KO
    assert rx_status(None, LR_SPEC) == RX_NONE and rx_status(-30, LR_SPEC) == RX_NONE
    assert rx_status(-14.5, LR_SPEC) == RX_LOW and rx_status(-14.4, LR_SPEC) == RX_OK
    assert rx_status(0.5, LR_SPEC) == RX_OK and rx_status(0.6, LR_SPEC) == RX_HIGH
    assert dbm_fr(-14.4) == "−14,4" and dbm_fr(0.5) == "+0,5" and dbm_fr(0) == "0"


def test_otdr_reading_and_bend_radius():
    assert math.isclose(otdr_distance_m(4.9e-6), 299_792_458 * 4.9e-6 / (2 * 1.468))
    assert round(otdr_distance_m(4.9e-6)) == 500
    assert break_position_m(562, 150) == 412 and E10_BREAK == 412 and X05_BREAK == 387
    assert otdr_event_kind(OtdrEvent(150, True, 0.4, 0.4)) == O_CONNECTOR
    assert otdr_event_kind(OtdrEvent(600, False, 0.05, 0.05)) == O_SPLICE
    assert otdr_event_kind(OtdrEvent(900, False, 0.1, 0.9)) == O_BEND
    assert otdr_event_kind(OtdrEvent(900, True, 0, 0, end=True)) == O_END
    assert not OTDR_EXAMPLE.broken and OTDR_EXAMPLE.end_m - OTDR_EXAMPLE.launch_m == OTDR_EXAMPLE.link_m
    points = trace_points(OTDR_EXAMPLE)
    xs = [x for x, _y in points]
    assert xs == sorted(xs) and points[0] == (0.0, 0.0)
    # la pente entre l'épissure (610 m) et la courbure (980 m) vaut 0,4 dB/km
    before_bend = next(y for x, y in points if x == 980)
    after_splice = [y for x, y in points if x == 610][-1]
    assert math.isclose(after_splice - before_bend, 0.37 * 0.4, abs_tol=1e-3)
    assert min_bend_radius_mm(8, pulling=False) == 80 and min_bend_radius_mm(8, pulling=True) == 160


def test_procedures_order():
    assert [t for t, _s in PROCEDURES] == [
        "Inspecter, nettoyer, inspecter un connecteur",
        "Poser et contrôler une liaison optique",
        "Diagnostiquer une liaison optique sans lien",
    ]
    clean = [label for label, _d in CLEAN_STEPS]
    assert clean.index("Inspecter") < clean.index("Nettoyer à sec") < clean.index("Réinspecter") < clean.index("Raccorder")
    assert clean[0] == "Couper la lumière"
    install = [label for label, _d in INSTALL_STEPS]
    assert install.index("Tirer") < install.index("Raccorder") < install.index("Contrôler") < install.index("Documenter")
    diag = [label for label, _d in DIAG_STEPS]
    assert diag.index("Modules") < diag.index("Polarité") < diag.index("Connecteurs") < diag.index("Mesurer")


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR17_FIGURES]
    assert len(keys) == len(set(keys)) == 9  # ticket : au moins 4 schémas ou documents
    for figure in PR17_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR17_FIGURES}
    cores = dict(re.findall(r'data-fibre="(\w+)" data-core-um="([\d,]+)"', by_key["pr17-coupe-fibre"].svg))
    assert cores == {"OM1": "62,5", "OM3": "50", "OS2": "9"}
    duplex = re.findall(r'data-fibre="(\d)" data-from="([\w-]+)" data-to="([\w-]+)"', by_key["pr17-polarite-duplex"].svg)
    assert duplex == [("1", "A-TX", "B-RX"), ("2", "B-TX", "A-RX"), ("1", "A-TX", "B-TX"), ("2", "A-RX", "B-RX")]
    ferrules = dict(re.findall(r'data-connector="(\w+)" data-ferrule-mm="([\d,]+)"', by_key["pr17-connecteurs"].svg))
    assert ferrules == {"LC": "1,25", "SC": "2,5", "ST": "2,5"}
    assert re.findall(r'data-polish="(\w+)" data-angle="(\d+)"', by_key["pr17-connecteurs"].svg) == [("UPC", "0"), ("APC", "8")]
    chain = re.findall(r'data-element="(\w+)" data-db="([\d,]+)"', by_key["pr17-chaine-liaison"].svg)
    assert [k for k, _d in chain] == [k for k, _l, _d in CHAIN_ELEMENTS]
    assert ("fibre", "0,32") in chain and chain.count(("connecteur", "0,75")) == 2 and chain.count(("epissure", "0,3")) == 2
    assert "2,42 dB" in by_key["pr17-chaine-liaison"].svg
    events = re.findall(r'data-event="([^"]+)" data-m="(\d+)"', by_key["pr17-trace-otdr"].svg)
    assert [(k, int(m)) for k, m in events] == [
        (escape(O_CONNECTOR), 150), (escape(O_SPLICE), 610), (escape(O_BEND), 980), (escape(O_END), 1380)]
    zones = re.findall(r'data-zone="([^"]+)" data-from="(-?[\d,]+)" data-to="(-?[\d,]+)"', by_key["pr17-puissance-recue"].svg)
    assert [z for z, *_r in zones] == [escape(s) for s in (RX_NONE, RX_LOW, RX_OK, RX_HIGH)]
    assert zones[2][1:] == ("-14,4", "0,5")
    for key, steps in (("pr17-procedure-nettoyage", CLEAN_STEPS), ("pr17-procedure-pose", INSTALL_STEPS),
                       ("pr17-procedure-diagnostic", DIAG_STEPS)):
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in by_key[key].svg, (key, label)


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 16 and len(EXAM_ITEMS) == 10  # ticket : ≥ 16 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 3), (KIND_CHOICE, 3), (KIND_CONNECT, 3), (KIND_MEASURE, 3),
                          (KIND_DIAG, 3), (KIND_SAFETY, 2)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert covered == REQ == set(plan.COURSE_SLOTS_BY_CODE["PR17"].requirement_ids)
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 5
    assert sum(1 for i in PRACTICE_ITEMS if i.documents) >= 6


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i].split(" — ")[0] for i in o.correct]

    assert ordered("E01") == [label for label, _d in CLEAN_STEPS]
    assert ordered("E02") == [label for label, _d in INSTALL_STEPS]
    assert ordered("E03") == [label for label, _d in DIAG_STEPS]

    def answers(key: str) -> dict[str, str]:
        c = by_key[key].classification
        return dict(zip(c.elements, (c.categories[i] for i in c.correct), strict=True))

    def find(mapping: dict[str, str], fragment: str) -> str:
        return next(v for k, v in mapping.items() if fragment in k)

    e04 = answers("E04")
    assert find(e04, "LOS") == RX_NONE and find(e04, "−31,0") == RX_NONE and find(e04, "−16,2") == RX_LOW
    assert find(e04, "+1,4") == RX_HIGH and find(e04, "−13,9") == RX_OK and find(e04, "−22,5") == RX_LOW
    e05 = answers("E05")
    assert find(e05, "À 150 m") == O_CONNECTOR and find(e05, "À 620 m") == O_SPLICE
    assert find(e05, "À 980 m") == O_BEND and find(e05, "coffret") == O_BEND and find(e05, "412 m") == O_END
    e06 = answers("E06")
    assert find(e06, "OM3, 180 m") == C_OK and find(e06, "OM2, 150 m") == C_REACH
    assert find(e06, "d'un côté") == C_PAIR and find(e06, "OS2, 40 m") == C_FIBRE and find(e06, "OM4, 90 m") == C_FIBRE
    assert find(e06, "OM1, 320 m") == C_REACH and find(e06, "1000BASE-LX") == C_OK
    e07 = answers("E07")
    assert find(e07, "62.5/125") == FAM_OLD_MM and find(e07, "violette") == FAM_LASER_MM
    assert find(e07, "SC/APC") == FAM_SM and find(e07, "gaine noire") == FAM_SM and find(e07, "OM2") == FAM_OLD_MM
    e08 = answers("E08")
    assert find(e08, "Lien neuf") == CAUSE_POLARITY and find(e08, "tache") == CAUSE_DIRTY
    assert find(e08, "850 nm") == CAUSE_MODULE and find(e08, "OM1 de 120 m") == CAUSE_REACH
    assert find(e08, "travaux") == CAUSE_BREAK and find(e08, "rebrassage") == CAUSE_POLARITY
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu, aucun classement trivial
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key
        if item.classification:
            correct = list(item.classification.correct)
            assert correct[: len(item.classification.categories)] != list(range(len(item.classification.categories))), item.key
            assert len(set(correct)) == len(item.classification.categories), item.key


def test_numbers_in_corrections_match_calculations():
    by_key = {i.key: i for i in PRACTICE_ITEMS + EXAM_ITEMS}
    text = lambda key: " ".join(by_key[key].correction)
    assert E09_MAX == 2.74 and E09_LOSSES == {"F1": 2.3, "F2": 2.05, "F3": 5.8, "F4": 2.6}
    assert "2,74 dB" in text("E09") and "F3 : 5,8 dB" in text("E09") and "3,06 dB" in text("E09")
    assert "412 m" in text("E10") and "2,36 dB" in text("E10") and "2,96 dB" in text("E10")
    assert E11_MAX == 1.85 and E11_LOSS_AB == 8.3 and "8,3 dB" in text("E11") and "1,85 dB" in text("E11")
    assert E12_LOSS == 3.18 and "3,18 dB" in text("E12") and "3,02 dB" in text("E12")
    assert "80 mm" in text("E14") and "160 mm" in text("E14")
    assert "2,34 dB" in text("X01") and "10,6 dB" in text("X02") and "1,57 dB" in text("X02")
    assert "82 m" in text("X04") and "387 m" in text("X05")
    assert X06_LOSS == 2.95 and X06_MAX == 2.64 and "0,31 dB" in text("X06")
    assert "60 mm" in text("X07") and "120 mm" in text("X07")
    assert X10_RX == -0.6 and X10_RX_AFTER == -5.6 and "−0,6 dBm" in text("X10") and "2,4 dB" in text("X10")


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("réflexion totale", "125 µm", "62,5 µm", "50 µm", "9 µm", "850", "1 310", "1 550", "infrarouge",
                  "invisible", "dispersion modale", "300 m", "400 m", "10 km", "lc", "1,25 mm", "2,5 mm", "apc",
                  "8°", "sfp+", "tx", "rx", "une seule extrémité", "0,75 db", "0,3 db", "0,4 db/km", "3,5 db/km",
                  "référence − lecture", "bobine amorce", "plus forte à 1 550 nm", "jamais regarder",
                  "photomètre", "récipient fermé", "ruban adhésif", "tapis sombre", "100 m", "pigtail",
                  "épissure par fusion", "aramide", "marquage", "isolation électrique", "poe"):
        assert right in text, right
    for wrong in ("regarder dans la fibre pour vérifier", "la fibre conduit le courant", "croiser les fibres aux deux extrémités corrige",
                  "un apc se raccorde sur un upc", "le cuivre tient 250 m", "la couleur suffit", "balayer les chutes à la main pour",
                  "monomode à 850 nm", "multimode : cœur de 9 µm", "une épissure perd plus à 1 550 nm"):
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
        "Cas 1 — Lien inversé", "Cas 2 — Connecteur sale", "Cas 3 — Mauvais module",
        "Cas 4 — Distance trop grande pour le module", "Cas 5 — Fibre cassée"]
    for title, _s, _steps, _conclusion in CASES:
        assert title in text, title
    assert text.count("Conclusion rédigée.") == 5
    assert "2,42 dB" in text and "−4 dBm" in text and "7,7 dB" in text and "412 m" in text and "2,97 dB" in text
    for i in (1, 2, 3):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr17_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "lumière", "cœur", "gaine", "monomode", "multimode", "portée", "norme", "module", "om", "os2",
        "lc", "sc", "sfp", "sfp+", "tx", "rx", "duplex", "longueur d'onde", "pertes", "atténuation",
        "connecteurs propres", "épissure", "pigtail", "brassage", "rayon de courbure",
        "cuivre", "coaxial", "parasites", "distance", "coût",
        "procédure de pose", "contrôle", "puissance", "photométrie", "otdr", "sécurité laser",
        "éclats", "ne jamais regarder",
        "lien inversé", "connecteur sale", "mauvais module", "distance trop grande", "cassée",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-21", "AP-22"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "convention du cours" in text.lower()
    for link in ("/uaa/ampcr-mc15", "/uaa/ampcr-pratique-pr13", "/uaa/ampcr-pratique-pr14", "/uaa/ampcr-pratique-pr15",
                 "/uaa/ampcr-pratique-pr16", f"/uaa/{PR17_SLUG}/practice", f"/uaa/{PR17_SLUG}/exam"):
        assert link in raw, link
    anchors = set(re.findall(r'id="(pr17-e\d\d)"', raw))
    assert anchors == {f"pr17-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr17-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr17_course_sections()]
    assert kinds[:12] == ["theory"] * 12
    assert kinds[12:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR17"]
    assert slot.ticket == 218 and slot.title == PR17_TITLE == PRACTICAL_COURSES_BY_CODE["PR17"].title


def test_seed_publishes_pr17_in_practical_module_idempotently(db_session):
    module, uaa = _pr17(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR17_TITLE and uaa.position == 17
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR17").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr17_course_sections())
    assert {"PR14", "PR15", "PR16", "PR17"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR16") < ordered.index("PR17") < ordered.index("PR20")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr17(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr17_specific():
    context = _pedagogical_context_for("PR17")
    assert context is get_practical_context("PR17")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("réflexion totale", "300 m OM3", "APC 8°", "TX d'un côté vers RX", "une seule extrémité",
                   "perte = référence − lecture", "1550 nm = courbure", "10 × diamètre", "ne jamais regarder"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "APC raccordé sur un UPC" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr17(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR17_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and "jc-pr-console" in html


def test_practical_home_and_matrix_show_pr17(client, db_session):
    _pr17(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR18 (#219) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR17"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr17(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR17"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr17(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR17", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr17(db_session)
    for _ in range(2):  # 18 exercices : deux sessions de 10 couvrent presque toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

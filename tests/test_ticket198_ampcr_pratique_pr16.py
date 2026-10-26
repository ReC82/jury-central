"""Ticket #198 — AMPCR pratique écrite, PR16 « Câble coaxial et BNC — impédance, fabrication et
diagnostic écrit ».

Couvre : valeurs techniques (50/75 Ω, limites 10BASE2/10BASE5, recopiées ici indépendamment du
code), modèle de bus (non-conformités, lectures d'ohmmètre, coefficients de réflexion, distances
de réflectomètre), schémas SVG dessinés depuis ces données (deux terminateurs 50 Ω, versions
fautives, 10BASE5 distinct du 10BASE2, accessibilité), réponses auto-corrigées, contenu du
cours (matière 1-12, 4 exemples, 16 exercices, mini-examen), banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr16_bank import (
    E02_CASES,
    E02_CORRECT,
    E06_CASES,
    E06_CORRECT,
    E10_SHOWN,
    E13_CORRECT,
    E13_READINGS,
    E14_DISTANCE,
    EXAM_ITEMS,
    KIND_CHOICE,
    KIND_DIAGNOSIS,
    KIND_PROCEDURE,
    KIND_SCHEMA,
    PRACTICE_ITEMS,
    READING_CATEGORIES,
    X05_DISTANCE,
    validate_items,
)
from app.v1.ampcr_pratique_pr16_course import PR16_TITLE, pr16_course_sections
from app.v1.ampcr_pratique_pr16_figures import (
    ATTACH_STUB,
    BUS_CUT,
    BUS_FAULT_FIGURES,
    BUS_MISSING_TERMINATOR,
    BUS_NO_TERMINATORS,
    BUS_OK,
    BUS_OK_FIGURE,
    BUS_SHORT,
    BUS_STUB_AND_GROUNDS,
    BUS_WRONG_IMPEDANCE,
    CABLE_IMPEDANCE,
    COMPARISON_FIGURE,
    CRIMP_STEPS,
    PR16_FIGURES,
    READINGS,
    STRIP_FIGURE,
    TDR_FIGURES,
    BusEnd,
    _stations_bus,
    bus_errors,
    ohmmeter_reading,
    reflection_coefficient,
    tdr_distance_m,
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

SLUG = "ampcr-pratique-pr16"

# Valeurs du cahier des charges du ticket #198 et des sources vérifiées (IEEE 802.3 cl. 8 et 10),
# recopiées ici indépendamment du code.
THIN = {"impedance": 50, "segment_m": 185, "stations": 30, "spacing_m": 0.5}
THICK = {"impedance": 50, "segment_m": 500, "transceivers": 100, "spacing_m": 2.5, "aui_m": 50}


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_text() -> str:
    return _text(" ".join(c for _t, c in pr16_course_sections())).lower()


def _pr16(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR16")
    return module, uaa


# =============================================================================================
# 1. Valeurs techniques et modèle de bus
# =============================================================================================


def test_impedances_of_cables():
    assert CABLE_IMPEDANCE["RG-58"] == THIN["impedance"] == 50
    assert CABLE_IMPEDANCE["RG-8"] == THICK["impedance"] == 50
    assert CABLE_IMPEDANCE["RG-59"] == CABLE_IMPEDANCE["RG-6"] == 75


def test_reflection_coefficients_and_tdr():
    assert reflection_coefficient(50, 50) == 0
    assert reflection_coefficient(None, 50) == 1
    assert reflection_coefficient(0, 50) == -1
    assert reflection_coefficient(75, 50) == pytest.approx(0.2)
    # d = VF × c × t / 2 ; c ≈ 0,2998 m/ns.
    assert tdr_distance_m(1000, 1.0) == pytest.approx(149.9, abs=0.1)
    assert E14_DISTANCE == pytest.approx(0.66 * 0.2998 * 520 / 2, abs=0.05)
    assert X05_DISTANCE == pytest.approx(0.66 * 0.2998 * 180 / 2, abs=0.05)


def test_reference_bus_is_conforming_and_has_two_50_ohm_terminators():
    assert bus_errors(BUS_OK) == []
    assert BUS_OK.first.terminator_ohm == BUS_OK.last.terminator_ohm == 50
    assert [BUS_OK.first.grounded, BUS_OK.last.grounded].count(True) == 1
    assert all(CABLE_IMPEDANCE[s.cable] == 50 for s in BUS_OK.spans)


def test_bus_rules_detect_each_fault():
    assert any("sans terminateur" in e for e in bus_errors(BUS_MISSING_TERMINATOR))
    errors = bus_errors(BUS_STUB_AND_GROUNDS)
    assert any("un seul point de terre" in e for e in errors) and any("T doit être sur la carte" in e for e in errors)
    errors = bus_errors(BUS_WRONG_IMPEDANCE)
    assert any("75 Ω" in e and "Terminateur" in e for e in errors) and any("RG-59" in e for e in errors)
    assert any("coupé" in e for e in bus_errors(BUS_CUT))
    names = tuple(f"P{i}" for i in range(1, THIN["stations"] + 2))
    big = _stations_bus(names, (7,) * (len(names) - 1), first=BusEnd(50), last=BusEnd(50))
    errors = bus_errors(big)
    assert any("185 m au plus" in e for e in errors) and any("30 au plus" in e for e in errors)
    short = _stations_bus(("A", "B"), (0.4,), first=BusEnd(50), last=BusEnd(50))
    assert any("0,5 m" in e for e in bus_errors(short))
    limit = _stations_bus(("A", "B"), (THIN["segment_m"],), first=BusEnd(50), last=BusEnd(50))
    assert bus_errors(limit) == []


def test_ohmmeter_readings_follow_the_physics():
    assert ohmmeter_reading(BUS_OK) == 25  # 50 ∥ 50
    assert ohmmeter_reading(BUS_MISSING_TERMINATOR) == 50
    assert ohmmeter_reading(BUS_CUT, 0) == 50 and ohmmeter_reading(BUS_CUT, 3) == 50
    assert ohmmeter_reading(BUS_SHORT) == 0
    assert ohmmeter_reading(BUS_NO_TERMINATORS) is None
    assert [v for _s, v, _m in READINGS] == [25, 50, 50, 0, None]


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_reference_bus_figure_shows_two_50_ohm_terminators_and_t_on_cards():
    svg = BUS_OK_FIGURE.svg
    assert re.findall(r'data-terminator="([^"]+)"', svg) == ["50", "50"]
    assert len(re.findall(r'data-ground="', svg)) == 1
    assert set(re.findall(r'data-attachment="([^"]+)"', svg)) == {"T"}
    assert len(re.findall(r"data-station=", svg)) == 4
    assert "Segment conforme" in svg and "Non-conformités" not in svg


def test_fault_figures_are_drawn_from_their_bus_and_flagged():
    expected = (BUS_MISSING_TERMINATOR, BUS_STUB_AND_GROUNDS, BUS_WRONG_IMPEDANCE, BUS_CUT)
    for figure, bus in zip(BUS_FAULT_FIGURES, expected, strict=True):
        assert "Non-conformités" in figure.svg and "fautif" in figure.title.lower()
        for error in bus_errors(bus):
            assert escape(error.split(" : ")[0]) in figure.svg, (figure.key, error)
    assert 'data-terminator="aucun"' in BUS_FAULT_FIGURES[0].svg
    assert 'data-attachment="stub"' in BUS_FAULT_FIGURES[1].svg and BUS_FAULT_FIGURES[1].svg.count("data-ground=") == 2
    assert 'data-terminator="75"' in BUS_FAULT_FIGURES[2].svg and "RG-59|" in BUS_FAULT_FIGURES[2].svg
    assert "câble coupé" in BUS_FAULT_FIGURES[3].svg


def test_comparison_keeps_10base5_distinct_and_video_at_75_ohm():
    svg = COMPARISON_FIGURE.svg
    panels = dict(re.findall(r'<g data-panel="([^"]+)">(.*?)</g>', svg, re.DOTALL))
    assert set(panels) == {"10BASE2", "10BASE5", "video-75"}
    assert "50 Ω" in panels["10BASE2"] and "BNC" in panels["10BASE2"] and "185 m" in panels["10BASE2"]
    assert "vampire" in panels["10BASE5"] and "AUI" in panels["10BASE5"] and "500 m" in panels["10BASE5"]
    assert "BNC" not in panels["10BASE5"] and ">T<" not in panels["10BASE5"]
    assert "75 Ω" in panels["video-75"] and ">T<" not in panels["video-75"]


def test_strip_figure_gives_no_universal_dimension():
    assert set(re.findall(r'data-dim="([A-C])"', STRIP_FIGURE.svg)) == {"A", "B", "C"}
    assert not re.search(r"\d+\s*mm", STRIP_FIGURE.svg)
    assert "notice" in STRIP_FIGURE.svg


def test_tdr_figures_direction_and_distance():
    opened, shorted = TDR_FIGURES
    assert 'data-event="ouvert"' in opened.svg and "réflexion positive" in opened.svg
    assert 'data-event="court-circuit"' in shorted.svg and "réflexion négative" in shorted.svg
    assert "39,6 m" in opened.svg and "24,7 m" in shorted.svg
    for figure in TDR_FIGURES:
        assert "fictive" in figure.caption


def test_figures_valid_accessible_and_unique():
    assert len(PR16_FIGURES) >= 12
    keys = [f.key for f in PR16_FIGURES]
    assert len(set(keys)) == len(keys)
    for figure in PR16_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "<title" in html and "<desc" in html and "schéma non officiel" in html
        assert "viewBox=\"0 0 380" in figure.svg or "viewBox=\"0 0 340" in figure.svg  # largeur mobile


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 15
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_SCHEMA) >= 5
    assert kinds.count(KIND_CHOICE) >= 4
    assert kinds.count(KIND_PROCEDURE) >= 3
    assert kinds.count(KIND_DIAGNOSIS) >= 3
    assert len(EXAM_ITEMS) == 10 and sum(i.total_points for i in EXAM_ITEMS) == 20
    assert {i.question_type for i in EXAM_ITEMS} <= {"short_answer", "long_answer", "document_analysis"}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(set(keys)) == len(keys)
    assert all("AP-35" in i.requirement_ids or "AP-18" in i.requirement_ids for i in PRACTICE_ITEMS + EXAM_ITEMS)


def test_auto_corrected_answers_are_technically_right():
    # E02 : conforme si et seulement si aucune règle du cours n'est violée.
    labels = [label for label, _bus in E02_CASES]
    conforming = {labels[i] for i, c in enumerate(E02_CORRECT) if c == 0}
    assert conforming == {
        "5 postes, 60 m de RG-58, T sur chaque carte, terminateur 50 Ω à chaque bout, une terre",
        "3 postes, 180 m de RG-58, terminateurs 50 Ω, une terre",
    }
    # E06 : usages → impédance, indépendamment des données de l'exercice.
    expected_75 = ("vidéosurveillance", "SDI", "télévision", "satellite")
    for (label, _ohm), index in zip(E06_CASES, E06_CORRECT, strict=True):
        assert index == (1 if any(k in label for k in expected_75) else 0), label
    # E13 : lectures et diagnostics.
    assert E13_READINGS == (25, 50, 0, None, 37.5, 50, 30)
    assert [READING_CATEGORIES[i].split(" :")[0] for i in E13_CORRECT] == [
        "Normal", "Un seul terminateur vu", "Court-circuit âme/blindage", "Aucun terminateur vu",
        "Terminateur de mauvaise valeur", "Un seul terminateur vu", "Terminateur de mauvaise valeur",
    ]
    # E10 : l'ordre attendu est celui de la procédure du cours.
    item = next(i for i in PRACTICE_ITEMS if i.key == "E10")
    assert [item.ordering.steps[i].split(" :")[0] for i in item.ordering.correct] == [n for n, _d in CRIMP_STEPS]
    assert list(E10_SHOWN) != list(range(len(CRIMP_STEPS)))


def test_no_false_technical_claims_anywhere():
    everything = _course_text() + " " + " ".join(
        " ".join((i.context, *i.correction, *(c.expected for c in i.criteria))) for i in PRACTICE_ITEMS + EXAM_ITEMS
    ).lower()
    assert "tous les bnc sont à 50" not in everything.replace("dire que « tous les bnc sont à 50 ω »", "").replace(
        "dire que tous les bnc sont à 50 ω", "").replace("« tous les bnc sont à 50 ω »", "")
    # 185 m / 500 m jamais inversés : chaque tableau porte sa propre limite.
    sections = dict(pr16_course_sections())
    ethernet = sections["PR16 — 5-7. Ethernet coaxial 10BASE2, 10BASE5 et liaisons vidéo 75 Ω"]
    thin, thick = ethernet.split("## 6. Ethernet épais")[0], ethernet.split("## 6. Ethernet épais")[1].split("## 7.")[0]
    assert f"**{THIN['segment_m']} m au plus**" in thin and "500 m" not in thin
    assert f"**{THICK['segment_m']} m au plus**" in thick and f"**{THICK['transceivers']} au plus**" in thick
    assert f"**{THICK['aui_m']} m au plus**" in thick and "185 m" not in thick and "BNC" in thick  # « pas de BNC »
    assert "pas de BNC" in thick
    # Aucune cote de dénudage chiffrée.
    assert not re.search(r"dénud\w*[^.]{0,40}\d+\s*mm", everything)
    # Le 10BASE2 n'est jamais présenté à 75 Ω.
    assert not re.search(r"10base2 (?:est|fonctionne|utilise)[^.]{0,30}75 ω", everything)
    assert "**10base2** : **50 ω**" in everything and "**vidéo (analogique, sdi)** : **75 ω**" in everything


def test_no_acronym_question_and_full_context():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.title, item.context, *item.instructions))
        assert not re.search(r"que signifie|que veut dire|développe[rz]? l'acronyme", text, re.IGNORECASE), item.key
        assert len(item.context) >= 150, item.key


def test_items_content_matches_existing_question_types():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        content = item_content(item, [1, 2][: len(item.documents)])
        validate_content(item.question_type, 1, content)


def test_four_examples_and_exam_not_in_course():
    text = _text(" ".join(c for _t, c in pr16_course_sections()))
    for example in ("Exemple 1 — Réaliser une liaison 10BASE2", "Exemple 2 — Diagnostiquer un terminateur absent",
                    "Exemple 3 — Détecter une mauvaise impédance", "Exemple 4 — Vérifier un connecteur mal serti"):
        assert example in text, example
    course = " ".join(content for _title, content in pr16_course_sections())
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


# =============================================================================================
# 4. Cours : toute la matière obligatoire (points 1 à 12 du ticket)
# =============================================================================================


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr16_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # 1 structure
        "âme", "diélectrique", "blindage", "tresse", "feuille", "gaine", "emi", "atténuation", "bande passante",
        "souplesse", "contraintes de pose",
        # 2 impédance
        "impédance caractéristique", "pas de la longueur", "50 ω", "75 ω", "existe en 50 ω et en 75 ω",
        "câble, connecteur, terminaison et équipement",
        # 3 réflexions
        "réflexion", "désadaptation", "terminaison absente", "terminaison erronée", "rupture", "connecteur défectueux",
        # 4 BNC
        "baïonnette", "quart de tour", "mâle", "femelle", "adaptateur en t", "terminateur", "à sertir",
        "à compression", "outils",
        # 5 10BASE2
        "10base2", "bus", "10 mb/s", "185 m", "rg-58", "deux terminateurs 50 ω", "30 au plus", "0,5 m au moins",
        "directement sur la carte", "un seul point", "une étoile",
        # 6 10BASE5
        "10base5", "500 m", "prise vampire", "transceiver", "aui", "n'est pas du 10base2",
        # 7 vidéo
        "sdi", "télévision", "la forme d'un connecteur ne suffit pas",
        # 8 fabrication
        "sécurité", "coupe franche", "cotes", "notice", "pas de cotes universelles", "contact central", "sertir",
        "contrôle visuel", "continuité", "court-circuit", "adaptation d'impédance",
        # 9 outils
        "coupe-câble", "dénudeur coaxial calibré", "pince à sertir", "multimètre", "testeur de câble coaxial", "tdr",
        # 10 schémas
        "câble ouvert", "connecteur mal serti", "mauvaise impédance", "volontairement faux",
        # 11 diagnostic
        "perte totale", "intermittent", "connecteur desserré", "blindage rompu", "câble écrasé",
        "non destructifs", "localiser", "réparer", "vérifier",
        # 12 sécurité et rapport
        "hors tension", "hypothèses", "validation", "historique",
    ):
        assert notion in text, notion


def test_course_flags_requirements_complements_and_fictive_supports():
    text = _text(" ".join(c for _t, c in pr16_course_sections()))
    for req in ("AP-35", "AP-18", "AP-20", "AP-C01"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr16_course_sections()]
    assert kinds.count("exam") == 1 and kinds.count("exercise") == 1 and kinds.count("example") == 1
    assert kinds[-1] == "info" and "summary" in kinds and "warning" in kinds


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_and_requirements():
    slot = plan.COURSE_SLOTS_BY_CODE["PR16"]
    assert slot.ticket == 198 and slot.title == PR16_TITLE == PRACTICAL_COURSES_BY_CODE["PR16"].title
    assert set(slot.requirement_ids) == {"AP-18", "AP-20", "AP-35"}
    assert "BNC" in plan.REQUIREMENTS_BY_ID["AP-35"].text


def test_seed_publishes_pr16_in_practical_module_idempotently(db_session):
    from app.v1.ampcr_pratique_pr16_course import PR16_OBSOLETE_TITLES

    assert not PR16_OBSOLETE_TITLES & {t for t, _c in pr16_course_sections()}
    module, uaa = _pr16(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR16_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR16").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr16_course_sections())
    assert {"PR06", "PR11", "PR15", "PR16"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr16(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr16_specific():
    context = _pedagogical_context_for("PR16")
    assert context is get_practical_context("PR16")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    assert "185 m" in notions and "500 m" in notions and "75 Ω" in notions and "terminateur 50 Ω aux deux extrémités" in notions
    assert "tous les BNC sont à 50 Ω" in context.constraints and "mot-clé" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr16(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR16_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html


def test_practical_home_and_matrix_show_pr16(client, db_session):
    _pr16(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "4 cours publiés" in home
    assert plan.requirement_status("AP-35", {"PR16"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr16(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR16"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr16(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR16", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr16(db_session)
    for _ in range(2):  # 16 exercices : deux sessions couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200


def test_stub_attachment_constant_used_in_bank():
    assert any(s.attachment == ATTACH_STUB for s in BUS_STUB_AND_GROUNDS.stations)

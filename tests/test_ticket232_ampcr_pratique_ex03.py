"""Ticket #232 — AMPCR pratique écrite, EX03 « Examen blanc écrit — câblage RJ45, BNC et fibre ».

Couvre : données des dossiers **recontrôlées ici** indépendamment (brochages T568A/T568B écrits
en dur, fiche du stagiaire, droit/croisé, choix des câbles, longueurs des liens, 10 Gb/s en Cat6,
rayons de courbure, traction et séparation, bus 10BASE2 et coefficient de réflexion, lectures
d'ohmmètre, portées optiques, bilan, photométrie, puissance reçue, trace du réflectomètre et
position de la cassure) ; schémas (validité, accessibilité, aucun verdict, fichiers statiques
identiques au SVG produit) ; questions (10 × 10 points = 100, réponses libres, 3 dossiers,
matière du ticket, exigences de l'emplacement, pas de question d'acronyme) ; sujet (version
candidat sans corrigé, lignes de réponse imprimables, barème global) ; banque, seed, navigation
(pas d'entraînement), session d'examen (corrigé masqué avant remise, schémas dans leurs
questions, note sur 100) ; EX01, EX02 et les cours PR inchangés.
Aucun appel IA réel : `FakeAIProvider` partout."""

import re

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    _document_layout,
    get_practical_context,
    import_practical_bank,
    is_practical_exam_code,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_ex03_bank import (
    ALL_ITEMS,
    DOSSIER_A,
    DOSSIER_B,
    DOSSIER_C,
    DOSSIER_DOCUMENTS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    ITEM_COURSES,
    ITEM_PARTS,
    PRACTICE_ITEMS,
    validate_items,
)
from app.v1.ampcr_pratique_ex03_course import EX03_SLUG, EX03_TITLE, ex03_course_sections
from app.v1.ampcr_pratique_ex03_figures import (
    CABLE_CHOICES,
    CERT_FIGURE_LINKS,
    CROSSOVER,
    EX03_FIGURES,
    L1_CHOICE,
    L1_MAX_LOSS,
    L1_RX_EXPECTED,
    L1_RX_STATUS,
    L2_CHOICE,
    LINK_CABLES,
    LONG_ERRORS,
    MADE_PLUG,
    MADE_PLUG_LINKS,
    MADE_PLUG_SPLIT,
    MUSEUM_BUS,
    MUSEUM_ERRORS,
    OHM_READINGS,
    OUTAGE_BEND_M,
    OUTAGE_BREAK_M,
    OUTAGE_KINDS,
    OUTAGE_SCREEN,
    OUTAGE_TRACE,
    PHOTO_LOSSES,
    PHOTO_VERDICTS,
    REPAIRED_MAX_LOSS,
    RUN_ERRORS,
    RUNS,
    SCREEN_WIDTH,
    SCREENS,
    STATIC_FIGURES,
    STRAIGHT,
    TEN_G_VERDICT,
    WRONG_PINS,
    WRONG_TERMINATOR_GAMMA,
    static_svg,
)
from app.v1.ampcr_pratique_visuals import render_figure, validate_figure
from app.v1.assets import STATIC_DIR
from app.v1.models import Question, QuestionnaireSession, SessionMode, User
from app.v1.question_engine import validate_content
from app.v1.session_service import _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-ex03"
MODULE_COURSES = {"PR13", "PR14", "PR15", "PR16", "PR17"}

# Brochages écrits en dur (TIA/EIA-568), indépendamment du code de l'application.
T568A_REF = ("blanc-vert", "vert", "blanc-orange", "bleu", "blanc-bleu", "orange", "blanc-marron", "marron")
T568B_REF = ("blanc-orange", "orange", "blanc-vert", "bleu", "blanc-bleu", "vert", "blanc-marron", "marron")


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _subject_raw() -> str:
    return " ".join(c for _t, c in ex03_course_sections())


def _item(key: str):
    return next(i for i in EXAM_ITEMS if i.key == key)


def _expected(key: str) -> str:
    item = _item(key)
    return " ".join(c.expected for c in item.criteria) + " " + " ".join(item.correction)


def _items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in EXAM_ITEMS
    ).lower()


def _ex03(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "EX03")
    return module, uaa


# =============================================================================================
# 1. Données des dossiers, recontrôlées indépendamment
# =============================================================================================


def test_plug_of_the_trainee_against_t568b():
    # Broches 4-5 et 7-8 permutées, chaque paire reste sur sa position.
    assert [p for p in range(1, 9) if MADE_PLUG[p - 1] != T568B_REF[p - 1]] == [4, 5, 7, 8] == list(WRONG_PINS)
    assert MADE_PLUG_SPLIT == ()
    assert sorted(MADE_PLUG) == sorted(T568B_REF)
    links = {a: MADE_PLUG.index(T568B_REF[a - 1]) + 1 for a in range(1, 9)}
    assert tuple(links.items()) == MADE_PLUG_LINKS == ((1, 1), (2, 2), (3, 3), (4, 5), (5, 4), (6, 6), (7, 8), (8, 7))
    expected = _expected("X01")
    assert "1 blanc/vert, 2 vert, 3 blanc/orange, 4 bleu, 5 blanc/bleu, 6 orange, 7 blanc/marron, 8 marron" in expected
    assert "1 blanc/orange, 2 orange, 3 blanc/vert, 4 bleu, 5 blanc/bleu, 6 vert, 7 blanc/marron, 8 marron" in expected
    assert "languette dessous" in expected and "4→5, 5→4, 7→8, 8→7" in expected


def test_straight_or_crossover():
    cables = list(LINK_CABLES.values())
    assert cables == [STRAIGHT, CROSSOVER, STRAIGHT, CROSSOVER]
    # Croisé A ↔ B : 1→3, 2→6, 3→1, 6→2, le reste droit.
    crossed = {a: T568B_REF.index(T568A_REF[a - 1]) + 1 for a in range(1, 9)}
    assert crossed == {1: 3, 2: 6, 3: 1, 4: 4, 5: 5, 6: 2, 7: 7, 8: 8}
    assert dict(CERT_FIGURE_LINKS) == {a: T568A_REF.index(T568B_REF[a - 1]) + 1 for a in range(1, 9)} == crossed
    assert "1→3, 2→6, 3→1, 6→2" in _expected("X02") and "Auto MDI-X" in _expected("X02")


def test_cable_choices():
    assert {ref: c.cable for ref, c in CABLE_CHOICES.items()} == {
        "L1": "Cat5e U/UTP",
        "L2": "Cat6A F/UTP",
        "L3": "Cat5e S/FTP",
        "L4": "Coaxial 75 Ω (RG-59)",
        "L5": "Fibre optique (PR17)",
    }
    assert CABLE_CHOICES["L4"].connector == "BNC 75 Ω"
    expected = _expected("X03")
    assert "100 m" in expected and "90 m" in expected and "55 m" in expected and "terre" in expected


def test_certification_lengths_and_10g():
    # 96 m de lien permanent (> 90) et 101 m de canal (> 100).
    assert LONG_ERRORS == ["lien permanent de 96 m > 90 m", "canal de 101 m > 100 m"]
    assert TEN_G_VERDICT == "Catégorie insuffisante"  # 10GBASE-T en Cat6 au-delà de 55 m
    expected = _expected("X04")
    assert "T568A" in expected and "T568B" in expected and "paires séparées" in expected and "broche 7" in expected


def test_pose_runs():
    # Rayon minimal : 4 × Ø (non écranté), 8 × Ø (écranté), 10 × Ø (coaxial) ; 110 N ; classe b = 100 mm.
    by_key = {run.name.split(" — ")[0]: run for run in RUNS}
    assert 4 * by_key["T1"].diameter_mm > by_key["T1"].bend_radius_mm
    assert 8 * by_key["T2"].diameter_mm <= by_key["T2"].bend_radius_mm and by_key["T2"].pull_n > 110
    assert by_key["T3"].power_distance_mm < 100 and not by_key["T3"].metal_divider
    assert 10 * by_key["T4"].diameter_mm > by_key["T4"].bend_radius_mm
    assert by_key["T5"].metal_divider
    assert [len(RUN_ERRORS[r.name]) for r in RUNS] == [1, 1, 1, 1, 0]
    expected = _expected("X05")
    assert "22,4 mm" in expected and "62,4 mm" in expected and "61 mm" in expected and "conforme" in expected
    assert "12-13 mm" in expected and "wiremap" in expected


def test_museum_bus_and_reflection():
    assert len(MUSEUM_ERRORS) == 4
    joined = " ".join(MUSEUM_ERRORS)
    assert "75 Ω" in joined and "RG-59" in joined and "0,5 m" in joined and "le T doit être sur la carte" in joined
    assert "un seul point de terre" not in joined  # une seule terre : conforme
    assert MUSEUM_BUS.length_m <= 185 and len(MUSEUM_BUS.stations) <= 30
    assert abs(WRONG_TERMINATOR_GAMMA - (75 - 50) / (75 + 50)) < 1e-9
    assert "20 %" in _expected("X06") and "25 Ω" in _expected("X06")


def test_ohmmeter_readings():
    assert [value for _d, _c, value in OHM_READINGS] == [25.0, 50.0, 0.0]  # 50 ∥ 50, un seul 50, court-circuit
    expected = _expected("X07")
    assert "185 m" in expected and "500 m" in expected and "2,5 m" in expected and "AUI" in expected


def test_fibre_choices():
    assert L1_CHOICE == "10GBASE-LR sur monomode OS2" and L2_CHOICE == "10GBASE-T sur Cat6A"
    expected = _expected("X08")
    # 10GBASE-SR : 400 m sur OM4 (< 420 m), 82 m sur OM2 (< 180 m) ; 1000BASE-SX : 550 m sur OM2.
    assert "400 m" in expected and "82 m" in expected and "550 m" in expected and "APC" in expected


def test_fibre_budget_photometry_and_rx():
    # 0,42 km × 0,4 + 2 × 0,75 + 2 × 0,3 = 2,268 dB.
    assert L1_MAX_LOSS == round(0.42 * 0.4 + 2 * 0.75 + 2 * 0.3, 2) == 2.27
    assert PHOTO_LOSSES == {"Fibre 1": 2.1, "Fibre 2": 4.62}
    assert PHOTO_VERDICTS == {"Fibre 1": "Conforme", "Fibre 2": "Non conforme : perte trop élevée"}
    assert L1_RX_EXPECTED == round(-2.1 - 2.27, 2) and -14.4 <= L1_RX_EXPECTED <= 0.5
    assert L1_RX_STATUS == "Dans la plage de la fiche"
    assert REPAIRED_MAX_LOSS == round(0.42 * 0.4 + 2 * 0.75 + 4 * 0.3, 2)


def test_outage_trace_and_ports():
    screen = "\n".join(OUTAGE_SCREEN)
    assert screen.count("DOWN") == 2 and "LOS" in screen and "−4,4 dBm" in screen and "−4,4 dBm" in _expected("X10")
    assert [k.split(" (")[0] for k in OUTAGE_KINDS] == ["Connecteur", "Courbure trop serrée", "Fin de fibre ou cassure"]
    assert OUTAGE_BREAK_M == OUTAGE_TRACE.end_m - OUTAGE_TRACE.launch_m == 175 < OUTAGE_TRACE.link_m
    assert OUTAGE_BEND_M == 130 and OUTAGE_TRACE.broken
    expected = _expected("X10")
    assert "175 m" in expected and "polarité" in expected and "60 mm" in expected and "120 mm" in expected


def test_screens_fit_the_width():
    for name, lines in SCREENS.items():
        assert all(len(line) <= SCREEN_WIDTH for line in lines), name


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_without_verdict():
    assert len({f.key for f in EX03_FIGURES}) == len(EX03_FIGURES) == 4
    for figure in EX03_FIGURES:
        assert validate_figure(figure) == []
        html = str(render_figure(figure))
        assert 'role="img"' in html and "schéma non officiel" in html
        assert "✓" not in figure.svg and "✗" not in figure.svg
    plug, _cert, bus, otdr = EX03_FIGURES
    assert "ORDRE FAUX" not in plug.svg and "Courbure" not in otdr.svg and "cassure" not in otdr.svg.lower()
    assert "il faut" not in bus.svg and "50 Ω" in bus.svg and "75 Ω" in bus.svg


def test_static_figure_files_are_the_generated_svg():
    assert len(STATIC_FIGURES) == 4
    for figure, path in STATIC_FIGURES:
        content = (STATIC_DIR / path).read_text()
        assert content == static_svg(figure)
        assert content.startswith("<svg ") and "xmlns=" in content and "<title>" in content


def test_schema_documents_point_to_static_files():
    images = {d.image for i in EXAM_ITEMS for d in i.documents if d.image}
    assert images == {path for _f, path in STATIC_FIGURES}
    x06 = _item("X06")
    layout = _document_layout(next(d for d in x06.documents if d.image))
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/ex03-bus-salle-retro.svg"
    assert "75 Ω" in layout["alt"] and "non officiel" in layout["notice"]


# =============================================================================================
# 3. Questions
# =============================================================================================


def test_items_valid_and_scored_on_100():
    assert validate_items() == []
    assert len(EXAM_ITEMS) == 10 and ALL_ITEMS == EXAM_ITEMS and PRACTICE_ITEMS == ()
    assert all(i.usage == "exam" and i.total_points == 10 for i in EXAM_ITEMS)
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 100
    assert all(i.question_type in ("long_answer", "document_analysis") for i in EXAM_ITEMS)
    assert [i.key for i in EXAM_ITEMS] == [f"X{n:02d}" for n in range(1, 11)]
    for item in EXAM_ITEMS:
        assert len(item.criteria) >= 3 and len(item.correction) >= 3
        assert set(ITEM_COURSES[item.key]) <= MODULE_COURSES
    assert {c for codes in ITEM_COURSES.values() for c in codes} == MODULE_COURSES


def test_three_dossiers_with_documents():
    for dossier in (DOSSIER_A, DOSSIER_B, DOSSIER_C):
        assert len(DOSSIER_DOCUMENTS[dossier]) >= 3
        items = [i for i in EXAM_ITEMS if ITEM_PARTS[i.key] == dossier]
        assert len(items) >= 2 and all(i.documents for i in items)
        used = {d.title for i in items for d in i.documents}
        assert used == {d.title for d in DOSSIER_DOCUMENTS[dossier]}  # chaque document sert


def test_ticket_subjects_are_all_evaluated():
    text = _items_text()
    for needle in (
        "t568a", "t568b", "broche", "orientation", "droit", "croisé", "auto mdi-x", "wiremap", "paires séparées",
        "cat5e", "cat6a", "100 m", "u/utp", "f/utp", "s/ftp", "bnc", "50 ω", "75 ω", "10base2", "terminateur",
        "10base5", "monomode", "multimode", "lc", "sc/apc", "10gbase-lr", "atténu", "db/km", "courbure", "traction",
        "procédure", "photomètre", "réflectomètre",
    ):
        assert needle in text, needle


def test_items_cover_the_slot_requirements():
    slot = plan.EXERCISE_SLOTS_BY_CODE["EX03"]
    assert slot.ticket == 232 and slot.title == EX03_TITLE == PRACTICAL_COURSES_BY_CODE["EX03"].title
    covered = {r for i in EXAM_ITEMS for r in i.requirement_ids}
    assert set(slot.requirement_ids) <= covered
    assert covered <= set(plan.REQUIREMENTS_BY_ID)
    # Module 3 du plan = PR13 → PR17 (PR18 appartient au module suivant).
    assert {c.code for c in plan.COURSE_SLOTS if c.module_key == slot.module_key} == MODULE_COURSES


def test_no_acronym_question_and_no_official_claim():
    for item in EXAM_ITEMS:
        prompt = item.prompt.lower()
        assert "que signifie" not in prompt and "développe" not in prompt
        assert "officiel" not in item.title.lower()
    # Le sujet ne donne pas les réponses : pas de brochage complet dans les énoncés.
    for item in EXAM_ITEMS:
        stated = " ".join((item.context, *item.instructions, *(d.content_text for d in item.documents)))
        assert "blanc/vert, vert, blanc/orange" not in stated and "4 × " not in stated


def test_items_content_matches_existing_question_types():
    for item in EXAM_ITEMS:
        ids = list(range(1, len(item.documents) + 1))
        content = item_content(item, ids)
        validate_content(item.question_type, 1, content)
        assert "Barème" in content["rubric"] and content["max_score"] == 10


# =============================================================================================
# 4. Sujet (version candidat)
# =============================================================================================


def test_subject_has_questions_without_corrections():
    raw = _subject_raw()
    for number, item in enumerate(EXAM_ITEMS, start=1):
        assert f"Question {number} — " in raw
        for step in item.correction:
            assert step[:60] not in raw
        for criterion in item.criteria:
            assert criterion.expected[:60] not in raw
    assert raw.count('class="jc-ex-answer"') == 10 and raw.count('class="jc-ex-dossier"') == 3
    assert "Corrigé de référence" not in raw and "<details" not in raw


def test_subject_presents_scoring_and_sources():
    text = _text(_subject_raw()).replace("**", "")
    assert "10 questions à réponse rédigée" in text and "sur 100" in text
    assert "pas la durée officielle" in text and "fictifs" in text
    assert "/uaa/ampcr-pratique-ex03/exam" in text and "Ctrl + P" in text
    for code in plan.EXERCISE_SLOTS_BY_CODE["EX03"].requirement_ids:
        assert code in text
    for code in MODULE_COURSES:
        assert f"/uaa/ampcr-pratique-{code.lower()}" in text


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(title) for title, _c in ex03_course_sections()]
    assert kinds == ["theory", "theory", "theory", "theory", "theory", "method", "info"]


# =============================================================================================
# 5. Banque, seed, pages, sessions
# =============================================================================================


def test_seed_publishes_ex03_after_pr17_idempotently(db_session):
    module, uaa = _ex03(db_session)
    assert uaa.slug == SLUG == EX03_SLUG and uaa.is_published and uaa.title == EX03_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="EX03").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(ex03_course_sections())
    from app.v1.parcours import listed_uaas

    codes = [u.code for u in listed_uaas(db_session.get(Module, module.id))]
    assert codes.index("EX03") == codes.index("PR17") + 1
    assert codes.index("EX02") == codes.index("PR12") + 1 and codes.index("EX01") == codes.index("PR06") + 1
    assert {"EX01", "EX02", "EX03"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_exam_reserve_only(db_session):
    module, uaa = _ex03(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert is_practical_exam_code("EX03") and not is_practical_exam_code("PR17")
    assert import_practical_bank(db_session, module, uaa) == 10
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert [question_usage(q) for q in questions] == ["exam"] * 10


def test_correction_context_is_ex03_specific():
    context = _pedagogical_context_for("EX03")
    assert context is get_practical_context("EX03") and context.course_key == SLUG
    assert context is not get_practical_context("EX02")
    notions = " ".join(context.allowed_notions)
    assert "T568B" in notions and "10BASE2" in notions and "0,75 dB" in notions and "réflectomètre" in notions
    assert "/100" in context.level and "mot-clé" in context.constraints


def test_subject_page_navigation_and_home(client, db_session):
    _ex03(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    assert "Sujet" in html and f'href="/uaa/{SLUG}/practice"' not in html and f"/uaa/{SLUG}/exam" in html
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in EX03_FIGURES}
    assert html.count('class="jc-ex-question"') == 10
    assert "examen blanc EX03" in html
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus\s+· \d examens blancs sur 6", home)  # EX04 (#233) publié ensuite
    assert client.get("/ampcr-pratique/matrice").status_code == 200
    pr17 = client.get("/uaa/ampcr-pratique-pr17").text
    assert 'href="/uaa/ampcr-pratique-pr17/practice"' in pr17


def test_practice_redirects_to_exam(authenticated_client, db_session):
    _ex03(db_session)
    response = authenticated_client.get(f"/uaa/{SLUG}/practice", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == f"/uaa/{SLUG}/exam"
    assert db_session.query(QuestionnaireSession).count() == 0


def test_exam_session_hides_corrections_and_scores_on_100(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _ex03(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="EX03", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert session.question_count == 10 and fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"EX03"}
    shown = set()
    for position in range(1, 11):
        page = authenticated_client.get(f"{session_url}?q={position}").text
        assert "Corrigé de référence" not in page and "Barème" not in page
        shown |= {path for _f, path in STATIC_FIGURES if path in page}
    assert shown == {path for _f, path in STATIC_FIGURES}  # les quatre schémas dans leurs questions
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-100" in html and "/ 100" in html and "data-score-on-20" in html

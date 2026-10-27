"""Ticket #203 — AMPCR pratique écrite, PR02 « Alimentation, connectique, compatibilité et
sécurité ».

Couvre : données normalisées **recalculées ici** indépendamment (tolérances ATX, brochages,
puissances PCIe, rendement, budget de puissance, +12 V, grille de compatibilité, relevés de
mesures) ; schémas SVG (validité, accessibilité, broches et barres cohérentes avec les
données, flux d'air) ; exercices et mini-examen (format du socle, réponses auto-corrigées,
pas de question d'acronyme, contexte complet) ; cours (matière du ticket, 4 cas résolus,
affirmations techniques justes, supports fictifs, cartes) ; banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

import re
from html import escape

import pytest

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_audit import proven_requirement_ids as audit_proven_ids
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    get_practical_context,
    import_practical_bank,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_pr02_bank import (
    E02_CATEGORIES,
    E04_LOSS,
    E04_WALL,
    E05_RECOMMENDED,
    E06_12V_NEED,
    E06_12V_WATTS,
    E07_OUT,
    E08_FAILED,
    E13_CATEGORIES,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_CALC,
    KIND_COMPAT,
    KIND_ID,
    KIND_PROCEDURE,
    KIND_SAFETY,
    KIND_SYMPTOM,
    KIND_WIRING,
    PRACTICE_ITEMS,
    REQ,
    X02_WALL,
    X03_RECOMMENDED,
    validate_items,
)
from app.v1.ampcr_pratique_pr02_course import PR02_SLUG, PR02_TITLE, pr02_course_sections
from app.v1.ampcr_pratique_pr02_figures import (
    AIRFLOW,
    AIRFLOW_FIGURE,
    ATX24_FIGURE,
    BUDGET_FIGURE,
    CASE1_CONFIG,
    CASE2_LOADS,
    CASE2_RECOMMENDED,
    CASE2_TOTAL,
    CASE4_MEASURES,
    EFFICIENCY_LEVELS,
    MOLEX_PINOUT,
    POWER_CONNECTORS,
    PR02_FIGURES,
    RAILS,
    RAILS_BY_NAME,
    SAFE_STEPS,
    SATA_MOLEX_FIGURE,
    SATA_POWER_PINOUT,
    SCREEN_WIDTH,
    SYMPTOM_TREE,
    VIDEO_STANDARDS,
    failed_checks,
    gpu_power_capacity,
    measure_lines,
    recommended_psu,
    tolerance_range,
    wall_power,
    within_tolerance,
)
from app.v1.ampcr_pratique_pr06_figures import ATX24_PINOUT, EPS8_PINOUT
from app.v1.ampcr_pratique_visuals import render_figure, validate_figure
from app.v1.models import Question, QuestionnaireSession, SessionMode
from app.v1.question_engine import validate_content
from app.v1.session_service import _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-pr02"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr02_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr02(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR02")
    return module, uaa


# =============================================================================================
# 1. Données de référence, recalculées indépendamment
# =============================================================================================


def test_atx_tolerances():
    expected = {"+12 V": (11.4, 12.6), "+5 V": (4.75, 5.25), "+3,3 V": (3.135, 3.465),
                "+5 VSB": (4.75, 5.25), "−12 V": (-13.2, -10.8)}
    assert {r.name: tolerance_range(r) for r in RAILS} == pytest.approx(expected)
    colors = {r.name: r.color for r in RAILS}
    assert colors == {"+12 V": "jaune", "+5 V": "rouge", "+3,3 V": "orange", "+5 VSB": "violet", "−12 V": "bleu"}
    rail12 = RAILS_BY_NAME["+12 V"]
    assert within_tolerance(rail12, 11.40) and not within_tolerance(rail12, 11.35)


def test_pinouts_match_wire_colors_and_counts():
    assert len(ATX24_PINOUT) == 24 and len(EPS8_PINOUT) == 8
    rail_color = {r.color: r.name for r in RAILS}
    for _n, signal, color in ATX24_PINOUT:
        if color in rail_color:
            assert signal.startswith(rail_color[color].split()[0]), (signal, color)
    assert [s for _n, s, _c in EPS8_PINOUT].count("+12 V") == 4
    assert [p[0] for p in SATA_POWER_PINOUT] == list(range(1, 16))
    sata = [s for _n, s, _c in SATA_POWER_PINOUT]
    assert sata.count("+3,3 V") == sata.count("+5 V") == sata.count("+12 V") == 3
    assert [(s, c) for _n, s, c in MOLEX_PINOUT] == [("+12 V", "jaune"), ("Masse", "noir"), ("Masse", "noir"), ("+5 V", "rouge")]
    pins = {name.split(" (")[0].split(",")[0]: n for name, n, *_r in POWER_CONNECTORS}
    assert pins["ATX 24 broches"] == 24 and pins["Alimentation SATA 15 broches"] == 15 and pins["Molex 4 broches"] == 4


def test_pcie_power_and_efficiency_and_budget():
    assert gpu_power_capacity() == 75 and gpu_power_capacity(pcie6=1) == 150 and gpu_power_capacity(pcie8=2) == 375
    gold = next(level for level in EFFICIENCY_LEVELS if level[0] == "Gold")
    assert gold[1:] == (87, 90, 87)
    assert all(b >= a and b >= c for _n, a, b, c in EFFICIENCY_LEVELS)  # meilleur vers 50 %
    assert wall_power(360, 90) == pytest.approx(400) == pytest.approx(E04_WALL) and E04_LOSS == pytest.approx(40)
    assert X02_WALL == pytest.approx(500)
    assert CASE2_TOTAL == sum(load.watts for load in CASE2_LOADS) == 422
    assert recommended_psu(422) == 550 and CASE2_RECOMMENDED == 650  # recommandation de la carte graphique
    assert E05_RECOMMENDED == 550 and X03_RECOMMENDED == 150
    assert E06_12V_WATTS == 540 and E06_12V_NEED == pytest.approx(500 / 12)


def test_compatibility_grid_and_measures():
    assert failed_checks(CASE1_CONFIG) == ["Mémoire ↔ carte", "SSD M.2 ↔ emplacement", "Bloc : puissance",
                                           "Bloc : connecteurs PCIe"]
    assert E08_FAILED == ["Carte mère ↔ boîtier", "Ventirad ↔ boîtier et socket"]
    assert E07_OUT == ["+5 V", "+5 VSB"]
    in_load = {name: within_tolerance(RAILS_BY_NAME[name], load) for name, _idle, load in CASE4_MEASURES}
    assert in_load == {"+12 V": False, "+5 V": True, "+3,3 V": True, "+5 VSB": True}
    assert all(within_tolerance(RAILS_BY_NAME[name], idle) for name, idle, _load in CASE4_MEASURES)
    assert max(len(line) for line in measure_lines(CASE4_MEASURES)) <= SCREEN_WIDTH


def test_video_rates():
    rates = {name: rate for name, rate, _e in VIDEO_STANDARDS}
    assert rates == {"HDMI 1.4": 10.2, "HDMI 2.0": 18, "HDMI 2.1": 48, "DisplayPort 1.2": 21.6,
                     "DisplayPort 1.4": 32.4, "DisplayPort 2.1": 80}


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR02_FIGURES]
    assert len(keys) == len(set(keys)) == 8
    for figure in PR02_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    assert re.findall(r'data-pin="(\d+)"', ATX24_FIGURE.svg) == [str(n) for n in range(1, 25)]
    sata_pins = re.findall(r'data-row="Alimentation SATA[^"]*" data-pin="(\d+)" data-signal="([^"]+)"', SATA_MOLEX_FIGURE.svg)
    assert [(int(n), s) for n, s in sata_pins] == [(n, s) for n, s, _c in SATA_POWER_PINOUT]
    watts = [int(w) for w in re.findall(r'data-watts="(\d+)"', BUDGET_FIGURE.svg)]
    assert watts[: len(CASE2_LOADS)] == [load.watts for load in CASE2_LOADS]
    assert watts[len(CASE2_LOADS)] == CASE2_TOTAL and watts[-1] == CASE2_RECOMMENDED
    flows = re.findall(r'data-flow="(in|out)" data-key="([^"]+)"', AIRFLOW_FIGURE.svg)
    assert flows == [(kind, key) for key, kind, *_r in AIRFLOW]
    assert {key for kind, key in flows if kind == "in"} >= {"front-1", "front-2"}
    assert len(SYMPTOM_TREE) == 4 and len(SAFE_STEPS) == 6


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 15 and len(EXAM_ITEMS) == 10
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ID, 2), (KIND_CALC, 3), (KIND_COMPAT, 3), (KIND_WIRING, 1),
                          (KIND_SAFETY, 2), (KIND_SYMPTOM, 2), (KIND_PROCEDURE, 1)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered and "AP-C02" in covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR02"].requirement_ids) == REQ | {"AP-C02"}


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}
    e02 = by_key["E02"].classification
    answers = dict(zip(e02.elements, (E02_CATEGORIES[c] for c in e02.correct), strict=True))
    assert answers["EPS 8 broches (4+4) marqué « CPU »"].startswith("Processeur")
    assert answers["12V-2x6 à 16 broches"] == "Carte graphique" and answers["ATX 24 broches (20+4)"].startswith("Carte mère")
    e13 = by_key["E13"].classification
    answers = dict(zip(e13.elements, (E13_CATEGORIES[c] for c in e13.correct), strict=True))
    for element, verdict in answers.items():
        dangerous = any(w in element for w in ("Ouvrir le bloc", "resté branché", "Percer", "adaptateur Molex"))
        assert (verdict == "Pratique dangereuse ou interdite") is dangerous, element
    e03 = by_key["E03"].ordering
    ordered = [e03.steps[i] for i in e03.correct]
    assert "débrancher le câble secteur" in ordered[0] and "bouton" in ordered[1] and "bracelet" in ordered[2]
    assert "tester en charge" in ordered[-1]


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("on n'ouvre jamais un bloc", "éteint n'est pas hors tension", "usb-c est une forme de connecteur",
                  "ne sont pas interchangeables", "même socket ne veut pas dire compatibilité garantie",
                  "une mesure conforme n'innocente pas", "même forme ne veut pas dire même interface",
                  "les câbles modulaires ne sont pas normalisés côté bloc"):
        assert right in text, right
    for wrong in ("ouvrir le bloc pour le réparer", "même socket donc compatible", "usb-c garantit",
                  "ddr4 et ddr5 sont compatibles", "eps et pcie sont interchangeables", "le plus puissant est le meilleur"):
        assert wrong not in text, wrong


def test_no_acronym_question_and_full_context():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.title, item.context, *item.instructions))
        assert not re.search(r"que signifie|que veut dire|développe[rz]? l'acronyme", text, re.IGNORECASE), item.key
        assert len(item.context) >= 150, item.key
        assert "officiel" not in item.title.lower(), item.key


def test_items_content_matches_existing_question_types():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        content = item_content(item, [1, 2][: len(item.documents)])
        validate_content(item.question_type, 1, content)


# =============================================================================================
# 4. Cours
# =============================================================================================


def test_four_resolved_cases_and_exam_not_in_course():
    text = _text(_course_raw())
    for case in ("Cas 1 — Déterminer la compatibilité d'une configuration", "Cas 2 — Dimensionner un bloc",
                 "Cas 3 — Repérer un mauvais branchement", "Cas 4 — Évaluer des symptômes d'alimentation"):
        assert case in text, case
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr02_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # alimentation AC/DC et bloc
        "courant alternatif", "courant continu", "230 v", "+5 vsb", "ps_on#", "pwr_ok",
        # puissance, rendement
        "puissance nominale", "p = u × i", "rendement", "80 plus", "gold", "50 % de charge",
        # connecteurs
        "atx 24 broches", "20+4", "eps 8 broches", "4+4", "pcie 6", "8 broches", "12v-2x6", "sata 15", "molex",
        # budget
        "budget", "marge", "palier", "recommandation",
        # refroidissement
        "flux d'air", "cpu_fan", "pwm", "semi-passif", "pâte thermique",
        # protections
        "surintensité", "court-circuit", "onduleur", "parafoudre",
        # sécurité
        "esd", "bracelet antistatique", "débrancher le câble secteur", "batterie", "gonfl", "bebat",
        "tournevis", "multimètre", "testeur d'alimentation", "condensateurs",
        # connectique
        "usb 3.2 gen 2", "usb-c", "hdmi 2.1", "displayport 1.4", "sata", "pcie", "m.2", "nvme", "clé",
        # compatibilité
        "ddr4", "ddr5", "socket", "am5", "lga1700", "atx", "microatx", "mini-itx", "sfx", "ça rentre",
        # dossiers
        "mauvais branchement", "symptômes", "procédure", "compte rendu",
        # encadrés
        "à l'écrit", "repère rapide", "glossaire", "objectifs",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-04", "AP-06", "AP-17", "AP-C02"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    for link in ("/uaa/ampcr-mc02", "/uaa/ampcr-mc05", "/uaa/ampcr-pratique-pr01", "/uaa/ampcr-pratique-pr06",
                 f"/uaa/{PR02_SLUG}/practice", f"/uaa/{PR02_SLUG}/exam"):
        assert link in raw, link


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr02_course_sections()]
    assert kinds[:13] == ["theory"] * 13
    assert kinds[13:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR02"]
    assert slot.ticket == 203 and slot.title == PR02_TITLE == PRACTICAL_COURSES_BY_CODE["PR02"].title


def test_seed_publishes_pr02_in_practical_module_idempotently(db_session):
    module, uaa = _pr02(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR02_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR02").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr02_course_sections())
    assert {"PR01", "PR02", "PR06", "PR11", "PR15", "PR16", "PR20", "PR24"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr02(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr02_specific():
    context = _pedagogical_context_for("PR02")
    assert context is get_practical_context("PR02")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    assert "±5 % sur +12 V" in notions and "USB-C = forme, pas vitesse" in notions
    assert "on peut ouvrir" in context.constraints and "mot-clé" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr02(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR02_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html


def test_practical_home_and_matrix_show_pr02(client, db_session):
    _pr02(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "cours publiés" in home  # PR03 (#204) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR02"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == audit_proven_ids()  # « validé » : preuves de l'audit #235
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr02(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR02"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr02(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR02", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr02(db_session)
    for _ in range(2):  # 16 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

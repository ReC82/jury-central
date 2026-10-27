"""Ticket #202 — AMPCR pratique écrite, PR01 « Structure d'un PC et identification des
composants ».

Couvre : données normalisées **recalculées ici** indépendamment (formats de carte mère et
emboîtement, contacts des barrettes, débits PCIe, unités binaires de `lsblk`, capacité en octets
du relevé PowerShell) ; schémas SVG (validité, accessibilité, plans numérotés cohérents, formats
à l'échelle, liaisons du schéma-bloc) ; exercices et mini-examen (format du socle, réponses
auto-corrigées, pas de question d'acronyme, contexte complet) ; cours (matière du ticket, 4 cas
résolus, distinction ROM/stockage, supports fictifs, cartes) ; banque, seed, pages et sessions.
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
from app.v1.ampcr_pratique_pr01_bank import (
    E02_CATEGORIES,
    E04_SSD_SHOWN,
    E06_NVME4,
    E11_CATEGORIES,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_CHOICE,
    KIND_ID,
    KIND_INVENTORY,
    KIND_PROCEDURE,
    PRACTICE_ITEMS,
    REQ,
    validate_items,
)
from app.v1.ampcr_pratique_pr01_course import PR01_SLUG, PR01_TITLE, pr01_course_sections
from app.v1.ampcr_pratique_pr01_figures import (
    BOARD_FIGURE,
    BOARD_PARTS,
    CASE2_INSTALLED_GIB,
    CASE2_SLOTS,
    CASE_FIGURE,
    CASE_PARTS,
    COMPATIBILITY_QUESTIONS,
    DATA_PATH_FIGURE,
    DATA_PATH_LINKS,
    DATA_PATH_NODES,
    FORM_FACTOR_FIGURE,
    FORM_FACTORS,
    INVENTORY_DISKS,
    MEMORY_MODULES,
    PCIE_GENERATIONS,
    PR01_FIGURES,
    REAR_PANEL_FIGURE,
    REAR_PORTS,
    SCREEN_WIDTH,
    USB_SPEEDS,
    binary_size,
    board_fits_case,
    lsblk_lines,
    memory_cim_lines,
    pcie_lane_gbytes,
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

SLUG = "ampcr-pratique-pr01"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr01_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr01(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR01")
    return module, uaa


# =============================================================================================
# 1. Données de référence, recalculées indépendamment
# =============================================================================================


def test_form_factors_match_specifications_and_nesting():
    assert {(f.name, f.width_mm, f.depth_mm, f.max_slots) for f in FORM_FACTORS} == {
        ("ATX", 305, 244, 7), ("microATX", 244, 244, 4), ("Mini-ITX", 170, 170, 1),
    }
    by_name = {f.name: f for f in FORM_FACTORS}
    for board in by_name.values():
        for case in by_name.values():
            fits = board.width_mm <= case.width_mm and board.depth_mm <= case.depth_mm
            assert board_fits_case(board.name, case.name) is fits, (board.name, case.name)


def test_memory_modules_contacts_and_voltages():
    expected = {("DDR3", "DIMM"): 240, ("DDR3", "SO-DIMM"): 204, ("DDR4", "DIMM"): 288,
                ("DDR4", "SO-DIMM"): 260, ("DDR5", "DIMM"): 288, ("DDR5", "SO-DIMM"): 262}
    assert {(m.generation, m.form): m.contacts for m in MEMORY_MODULES} == expected
    volts = {m.generation: m.voltage for m in MEMORY_MODULES}
    assert volts["DDR4"] == "1,2 V" and volts["DDR5"] == "1,1 V" and volts["DDR3"].startswith("1,5 V")


def test_pcie_and_usb_rates():
    # 128b/130b : débit utile = GT/s × 128/130 / 8 (Go/s, un sens, une ligne)
    for version, gt in PCIE_GENERATIONS:
        assert abs(pcie_lane_gbytes(gt) - gt * 0.12307692) < 1e-6, version
    assert [round(pcie_lane_gbytes(gt) * 4, 1) for _v, gt in PCIE_GENERATIONS] == [3.9, 7.9, 15.8]
    assert E06_NVME4 == "7,9"
    speeds = {name: gbits for name, _old, gbits, _c in USB_SPEEDS}
    assert speeds == {"USB 2.0": 0.48, "USB 3.2 Gen 1": 5, "USB 3.2 Gen 2": 10, "USB 3.2 Gen 2x2": 20, "USB4": 40}


def test_lsblk_capture_uses_binary_units_and_data():
    assert binary_size(500 * 10**9) == "465.7G" == E04_SSD_SHOWN
    assert binary_size(2 * 10**12) == "1.8T" and binary_size(10**12) == "931.3G" and binary_size(64 * 10**9) == "59.6G"
    lines = lsblk_lines(INVENTORY_DISKS)
    assert lines[1].split() == ["NAME", "TRAN", "ROTA", "SIZE", "MODEL"]
    for disk, line in zip(INVENTORY_DISKS, lines[2:], strict=True):
        name, tran, rota, size, *_model = line.split()
        assert (name, tran, int(rota)) == (disk.name, disk.tran, disk.rota)
        value, unit = float(size[:-1]), size[-1]
        unit_bytes = 1024 ** ("KMGT".index(unit) + 1)
        assert abs(value * unit_bytes - disk.size_bytes) <= 0.05 * unit_bytes  # arrondi à une décimale
    assert {d.tran for d in INVENTORY_DISKS if d.rota == 1} == {"sata"}


def test_memory_capture_lists_only_detected_modules():
    lines = memory_cim_lines(CASE2_SLOTS)
    rows = [line.split() for line in lines[5:]]
    assert rows == [["DIMM_A2", str(8 * 1024**3), "4800"]]
    assert sum(int(r[1]) for r in rows) // 1024**3 == 8 < CASE2_INSTALLED_GIB


def test_every_capture_fits_a_mobile_screen():
    captures = [lsblk_lines(INVENTORY_DISKS), memory_cim_lines(CASE2_SLOTS)]
    captures += [d.content_text.splitlines() for i in PRACTICE_ITEMS + EXAM_ITEMS for d in i.documents
                 if d.kind == "console"]
    assert captures
    for capture in captures:
        assert max(len(line) for line in capture) <= SCREEN_WIDTH


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR01_FIGURES]
    assert len(keys) == len(set(keys)) == 8
    for figure in PR01_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_numbered_plans_match_their_legends():
    for figure, parts in ((BOARD_FIGURE, BOARD_PARTS), (CASE_FIGURE, CASE_PARTS)):
        numbers = [n for _p, n in parts]
        assert numbers == list(range(1, len(parts) + 1))
        assert re.findall(r'data-number="(\d+)"', figure.svg) == [str(n) for n in numbers]
        for part, number in parts:
            assert f"{number} {part.label}" in figure.alt
            assert 0 <= part.x and part.x + part.w <= 380
    rects = [p for p, _n in BOARD_PARTS]
    for i, a in enumerate(rects):  # aucune zone du plan de carte ne chevauche une autre
        for b in rects[i + 1:]:
            assert a.x + a.w <= b.x or b.x + b.w <= a.x or a.y + a.h <= b.y or b.y + b.h <= a.y, (a.key, b.key)
    ports = re.findall(r'data-port="(\d+)"', REAR_PANEL_FIGURE.svg)
    assert ports == [str(n) for n, *_r in REAR_PORTS]


def test_form_factor_figure_is_drawn_to_scale():
    for form in FORM_FACTORS:
        match = re.search(rf'data-form="{form.name}"[^>]*width="(\d+)" height="(\d+)"', FORM_FACTOR_FIGURE.svg)
        assert match and (int(match[1]), int(match[2])) == (form.width_mm, form.depth_mm), form.name


def test_data_path_links_reach_processor_or_chipset():
    keys = {n.key for n in DATA_PATH_NODES}
    links = {(link.a, link.b): link.label for link in DATA_PATH_LINKS}
    assert all(a in keys and b in keys for a, b in links)
    assert links[("ram", "cpu")] == "DDR" and links[("gpu", "cpu")] == "PCIe x16" and links[("nvme", "cpu")] == "PCIe x4"
    assert links[("chipset", "sata")] == "SATA" and ("cpu", "chipset") in links
    assert len(re.findall(r"data-link=", DATA_PATH_FIGURE.svg)) == len(DATA_PATH_LINKS)
    assert "ne transporte aucune donnée" in DATA_PATH_FIGURE.caption
    assert len(COMPATIBILITY_QUESTIONS) == 5


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 15 and len(EXAM_ITEMS) == 10
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ID, 4), (KIND_CHOICE, 5), (KIND_INVENTORY, 1), (KIND_PROCEDURE, 1)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered and "AP-C02" in covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR01"].requirement_ids) == REQ


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}
    e02 = by_key["E02"].classification
    answers = dict(zip(e02.elements, (E02_CATEGORIES[c] for c in e02.correct), strict=True))
    assert answers["Puce flash de la carte mère qui contient le firmware UEFI"].startswith("Mémoire non volatile du firmware")
    assert answers["SSD NVMe de 1 To"].startswith("Stockage") and answers["Cache L3 intégré au processeur"].startswith("Mémoire volatile")
    e11 = by_key["E11"].classification
    answers = dict(zip(e11.elements, (E11_CATEGORIES[c] for c in e11.correct), strict=True))
    assert answers["Scanner à plat"] == "Périphérique d'entrée" and answers["Vidéoprojecteur"] == "Périphérique de sortie"
    assert answers["Casque-micro"] == "Périphérique d'entrée et de sortie"
    e03 = by_key["E03"].ordering
    ordered = [e03.steps[i] for i in e03.correct]
    assert "lues sur le SSD" in ordered[0] and "en mémoire vive" in ordered[2] and "écran" in ordered[-1]


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("même socket ne veut pas dire compatibilité garantie", "la rom n'est pas du stockage",
                  "usb-c est une forme de connecteur", "ne sont pas interchangeables",
                  "ce n'est pas une panne", "rétrocompatible"):
        assert right in text, right
    for wrong in ("même socket donc compatible", "la rom contient le système", "usb-c garantit",
                  "ddr4 et ddr5 sont compatibles", "le bios est sur le disque"):
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
    for case in ("Cas 1 — Identifier les éléments d'une unité centrale", "Cas 2 — Interpréter un inventaire",
                 "Cas 3 — Choisir une carte mère de remplacement", "Cas 4 — Justifier l'installation d'une carte graphique"):
        assert case in text, case
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr01_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # boîtier et formats
        "atx", "microatx", "mini-itx", "305 × 244 mm", "flux d'air", "hauteur maximale du ventirad",
        # carte mère
        "socket", "lga", "pga", "chipset", "vrm", "eps", "liste des processeurs pris en charge",
        # processeur et refroidissement
        "puissance thermique", "partie graphique intégrée", "pâte thermique", "cpu_fan", "ventirad",
        # mémoires
        "dimm", "so-dimm", "ddr4", "ddr5", "rom", "volatile", "encoche-détrompeur", "double canal", "ecc",
        # firmware
        "bios", "uefi", "post", "pile cmos", "secure boot",
        # stockage
        "disque dur", "ssd sata", "nvme", "m.2", "2280", "unités binaires",
        # alimentation et carte graphique
        "atx 24 broches", "pcie 8 broches", "75 w", "longueur",
        # ports
        "usb 3.2 gen 2", "hdmi", "displayport", "rj45", "jack", "usb 3.x (19 broches)",
        # périphériques et pilotes
        "entrée-sortie", "envoie des informations au pc", "entrée et sortie", "pilote", "architecture", "gestionnaire de périphériques",
        # compatibilité et démarche
        "compatibilité", "ça rentre", "observer", "inventaire", "bracelet antistatique", "sachet antistatique",
        "débrancher le secteur", "ne jamais forcer",
        # encadrés
        "à l'écrit", "repère rapide", "glossaire", "objectifs",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-01", "AP-02", "AP-05", "AP-07", "AP-17", "AP-C02"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    for link in ("/uaa/ampcr-mc01", "/uaa/ampcr-mc02", "/uaa/ampcr-mc03", "/uaa/ampcr-mc04", "/uaa/ampcr-mc07",
                 "/uaa/ampcr-mc12", "/uaa/ampcr-pratique-pr06", f"/uaa/{PR01_SLUG}/practice", f"/uaa/{PR01_SLUG}/exam"):
        assert link in raw, link


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr01_course_sections()]
    assert kinds[:13] == ["theory"] * 13
    assert kinds[13:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR01"]
    assert slot.ticket == 202 and slot.title == PR01_TITLE == PRACTICAL_COURSES_BY_CODE["PR01"].title


def test_seed_publishes_pr01_in_practical_module_idempotently(db_session):
    module, uaa = _pr01(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR01_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR01").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr01_course_sections())
    assert {"PR01", "PR06", "PR11", "PR15", "PR16", "PR20", "PR24"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr01(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr01_specific():
    context = _pedagogical_context_for("PR01")
    assert context is get_practical_context("PR01")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    assert "ROM = puce flash du firmware" in notions and "USB-C = forme, pas débit" in notions
    assert "même socket donc compatible" in context.constraints and "mot-clé" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr01(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR01_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html  # tableaux comparatifs rendus


def test_practical_home_and_matrix_show_pr01(client, db_session):
    _pr01(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "cours publiés" in home  # PR02 (#203) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR01"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == audit_proven_ids()  # « validé » : preuves de l'audit #235
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr01(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR01"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr01(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR01", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr01(db_session)
    for _ in range(2):  # 16 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

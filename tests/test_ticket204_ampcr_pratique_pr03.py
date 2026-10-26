"""Ticket #204 — AMPCR pratique écrite, PR03 « Montage et démontage d'un PC — procédure
écrite ».

Couvre : données de référence **recontrôlées ici** indépendamment (cinq procédures, brochage de
façade Intel, entretoises, visserie, écarts d'inventaire, seuil de température) ; schémas SVG
(validité, accessibilité, broches, entretoises et étapes cohérentes avec les données) ;
exercices et mini-examen (format du socle, remises en ordre et classements auto-corrigés, pas
de question d'acronyme, contexte complet, aucune manipulation sous tension) ; cours (matière du
ticket, 5 procédures, 4 cas résolus, affirmations techniques justes, supports fictifs, cartes) ;
banque, seed, pages et sessions. Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr03_bank import (
    E05_CATEGORIES,
    E06_CATEGORIES,
    E07_EXTRA,
    E07_MISSING,
    E11_GAPS,
    E13_VERDICTS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_BOOT,
    KIND_ERROR,
    KIND_JUSTIFY,
    KIND_ORDER,
    KIND_PROCEDURE,
    PRACTICE_ITEMS,
    REQ,
    validate_items,
)
from app.v1.ampcr_pratique_pr03_course import PR03_SLUG, PR03_TITLE, pr03_course_sections
from app.v1.ampcr_pratique_pr03_figures import (
    ASSEMBLY_STEPS,
    BOOT_TREE,
    CASE3_DETECTED,
    CASE3_EXPECTED,
    CASE3_SCREEN,
    CASE4_AFTER,
    CASE4_BEFORE,
    CASE4_LIMIT,
    CASE_POSITION_KEYS,
    CPU_STEPS,
    DISASSEMBLY_STEPS,
    E07_BOARD_HOLES,
    E07_STANDOFFS,
    FIRST_BOOT_STEPS,
    FRONT_PANEL_FIGURE,
    FRONT_PANEL_PINS,
    PR03_FIGURES,
    PREP_STEPS,
    PROCEDURES,
    SCREEN_WIDTH,
    SCREWS,
    STANDOFF_FIGURE,
    STATUS_EXTRA,
    STATUS_MISSING,
    STATUS_OK,
    VISUAL_CHECKS,
    inventory_gaps,
    panel_pins_for,
    standoff_status,
    temperature_verdict,
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

SLUG = "ampcr-pratique-pr03"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr03_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr03(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR03")
    return module, uaa


# =============================================================================================
# 1. Données de référence, recontrôlées indépendamment
# =============================================================================================


def test_front_panel_follows_intel_layout():
    # Guide Intel « Front Panel I/O Connectivity Design Guide » : 2 × 5, broche 10 = clé.
    signals = {p.number: p.signal for p in FRONT_PANEL_PINS}
    assert sorted(signals) == list(range(1, 11))
    assert signals[1] == "HDD_LED+" and signals[3] == "HDD_LED−"
    assert signals[2] == "PLED+" and signals[4] == "PLED−"
    assert panel_pins_for("bouton Power") == (6, 8) and panel_pins_for("bouton Reset") == (5, 7)
    assert signals[10] == "clé" and signals[9] == "+5 V"
    polarized = {p.number for p in FRONT_PANEL_PINS if p.polarized}
    assert polarized == {1, 2, 3, 4}  # LED seulement ; boutons non polarisés


def test_standoffs_one_per_hole_and_none_elsewhere():
    status = standoff_status(E07_BOARD_HOLES, E07_STANDOFFS)
    assert set(status) == set(CASE_POSITION_KEYS) and len(CASE_POSITION_KEYS) == 12
    extra = sorted(E07_STANDOFFS - E07_BOARD_HOLES)
    missing = sorted(E07_BOARD_HOLES - E07_STANDOFFS)
    assert E07_EXTRA == extra == ["B", "J", "K", "L"] and E07_MISSING == missing == ["E"]
    assert all(status[k] == STATUS_OK for k in E07_BOARD_HOLES & E07_STANDOFFS)
    assert {status[k] for k in extra} == {STATUS_EXTRA} and status["E"] == STATUS_MISSING
    with pytest.raises(ValueError):
        standoff_status(frozenset({"Z"}), frozenset())


def test_screws_and_checks():
    screws = {what: screw for what, screw, _n in SCREWS}
    assert screws["Bloc d'alimentation"].startswith("6-32")
    assert screws["SSD ou disque 2,5 pouces"] == "M3" and screws["SSD M.2"].startswith("M2")
    assert "6-32" in screws["Carte mère sur ses entretoises"] and "M3" in screws["Carte mère sur ses entretoises"]
    checks = " ".join(c for _w, c in VISUAL_CHECKS)
    for word in ("vis", "film", "clic", "EPS", "ATX 24", "ventilateur", "PCIe"):
        assert word in checks, word


def test_procedures_and_inventory_and_temperatures():
    assert len(PROCEDURES) == 5
    assert [len(s) for _t, s in PROCEDURES] == [len(PREP_STEPS), len(ASSEMBLY_STEPS), len(CPU_STEPS),
                                              len(DISASSEMBLY_STEPS), len(FIRST_BOOT_STEPS)]
    labels = [label for label, _d in ASSEMBLY_STEPS]
    assert labels.index("Processeur") < labels.index("Carte mère") < labels.index("Carte graphique") < labels.index("Câbles")
    assert "débranché" in PREP_STEPS[2][1] and "Bracelet" in PREP_STEPS[4][1]
    assert "film" in CPU_STEPS[5][1] and "croix" in CPU_STEPS[5][1] and "CPU_FAN" in CPU_STEPS[6][1]
    assert "jamais en tirant" in DISASSEMBLY_STEPS[5][1]
    assert inventory_gaps(CASE3_EXPECTED, CASE3_DETECTED) == ["mémoire", "stockage", "ventilateur CPU"]
    assert inventory_gaps(CASE3_EXPECTED, CASE3_EXPECTED) == []
    assert E11_GAPS == ["mémoire", "stockage"]
    assert max(len(line) for line in CASE3_SCREEN) <= SCREEN_WIDTH
    assert f"{CASE3_DETECTED.memory_gb * 1024} Mo" in " ".join(CASE3_SCREEN)
    assert temperature_verdict(95, 95) == "anormal" and temperature_verdict(86, 95) == "à surveiller"
    assert temperature_verdict(74, 95) == "normal"
    assert temperature_verdict(CASE4_BEFORE[-1][1], CASE4_LIMIT) == "anormal"
    assert all(temperature_verdict(t, CASE4_LIMIT) == "normal" for _m, t in CASE4_AFTER)
    assert E13_VERDICTS[-1] == "anormal"


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR03_FIGURES]
    assert len(keys) == len(set(keys)) == 9
    for figure in PR03_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    pins = re.findall(r'data-pin="(\d+)" data-signal="([^"]+)"', FRONT_PANEL_FIGURE.svg)
    assert [(int(n), s) for n, s in pins] == [(p.number, escape(p.signal)) for p in FRONT_PANEL_PINS]
    positions = re.findall(r'data-position="([A-L])" data-status="([^"]+)"', STANDOFF_FIGURE.svg)
    assert dict(positions) == standoff_status(E07_BOARD_HOLES, E07_STANDOFFS)
    by_key = {f.key: f for f in PR03_FIGURES}
    for key, steps in (("pr03-preparer-poste", PREP_STEPS), ("pr03-ordre-montage", ASSEMBLY_STEPS),
                       ("pr03-processeur-ventirad", CPU_STEPS), ("pr03-demontage", DISASSEMBLY_STEPS),
                       ("pr03-premier-demarrage", FIRST_BOOT_STEPS)):
        svg = by_key[key].svg
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in svg, (key, label)
    assert by_key["pr03-pannes-premier-demarrage"].svg.count("data-step=") == len(BOOT_TREE) == 5


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 15 and len(EXAM_ITEMS) == 10
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 4), (KIND_ERROR, 4), (KIND_JUSTIFY, 3), (KIND_BOOT, 3), (KIND_PROCEDURE, 1)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered and "AP-C02" in covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR03"].requirement_ids) == REQ | {"AP-C02"}


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i] for i in o.correct]

    assert [s.split(" — ")[0] for s in ordered("E01")] == [label for label, _d in PREP_STEPS]
    assert [s.split(" — ")[0] for s in ordered("E03")] == [label for label, _d in CPU_STEPS]
    e02 = ordered("E02")
    assert "processeur" in e02[0] and "barrettes" in e02[1] and "pâte" in e02[2]
    assert "carte graphique" in e02[-2] and e02[-1].startswith("Brancher")
    e04 = ordered("E04")
    assert "autorisation" in e04[0] and "débrancher le secteur" in e04[1] and "vérifier" in e04[-1]
    e05 = by_key["E05"].classification
    answers = dict(zip(e05.elements, (E05_CATEGORIES[c] for c in e05.correct), strict=True))
    for element, verdict in answers.items():
        wrong = any(w in element for w in ("poussé", "au doigt", "sans comparer", "ouvert pour"))
        assert (verdict == "Erreur à corriger") is wrong, element
    e06 = by_key["E06"].classification
    answers = dict(zip(e06.elements, (E06_CATEGORIES[c] for c in e06.correct), strict=True))
    assert answers["Aucune vis ni entretoise libre dans le boîtier"].startswith("Contrôle visuel")
    assert answers["Mémoire totale égale à la somme des barrettes"].startswith("Lecture dans l'UEFI")
    assert answers["Test mémoire en plusieurs passes sans erreur"].startswith("Test sous le système")
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("éteint n'est pas hors tension", "on ne force jamais", "une entretoise sous chaque trou",
                  "film", "en croix", "la pâte se renouvelle", "le manuel de la carte fait foi",
                  "un bloc d'alimentation ne s'ouvre jamais", "on ne coupe pas", "un seul changement à la fois"):
        assert right in text, right
    for wrong in ("ouvrir le bloc pour", "la pâte peut être réutilisée", "appuyer fort sur le processeur",
                  "les boutons sont polarisés", "sous tension, retirer", "tirer fort sur le ventirad pour"):
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


def test_four_resolved_cases_five_procedures_and_exam_not_in_course():
    text = _text(_course_raw())
    for case in ("Cas 1 — Rédiger la procédure complète de montage", "Cas 2 — Démonter un PC pour remplacer le ventirad",
                 "Cas 3 — Corriger un premier démarrage incomplet", "Cas 4 — Surchauffe après un montage"):
        assert case in text, case
    for i in range(1, 6):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr03_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # préparation
        "poste", "outillage", "ph1", "ph2", "bracelet antistatique", "tapis antistatique", "inventaire", "photos",
        "sauvegarde", "autorisation", "état initial", "fiche d'intervention", "numéro de série",
        # compatibilité
        "compatibilité", "socket", "ddr5", "ça rentre",
        # ordre de montage
        "ordre", "entretoise", "plaque d'e/s", "lga", "pga", "capot", "triangle", "pâte thermique", "noisette",
        "ventirad", "cpu_fan", "barrette", "a2 et b2", "m.2", "30°", "bloc d'alimentation", "carte graphique",
        "pcie x16", "atx 24", "eps", "façade", "power sw", "reset", "led", "polarisé", "usb 3", "hd_audio",
        # contrôle et premier démarrage
        "contrôle visuel", "post", "uefi", "entraîne la mémoire", "xmp", "memtest86", "températures", "smart",
        # câbles et flux d'air
        "gestion des câbles", "flux d'air", "derrière le plateau",
        # démontage
        "ordre inverse", "visserie", "6-32", "m3", "loquet", "clip", "collé", "alcool isopropylique",
        # remplacement et pannes
        "remplacer", "remonter", "premier démarrage", "court-circuit", "pas d'image", "surchauffe",
        "compte rendu",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion
    # sécurité : aucune manipulation sous tension, bloc jamais ouvert
    assert "aucune manipulation ne se fait sous tension" in text and "un bloc d'alimentation ne s'ouvre jamais" in text


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-14", "AP-C02"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    for link in ("/uaa/ampcr-mc05", "/uaa/ampcr-mc06", "/uaa/ampcr-pratique-pr01", "/uaa/ampcr-pratique-pr02",
                 "/uaa/ampcr-pratique-pr06", f"/uaa/{PR03_SLUG}/practice", f"/uaa/{PR03_SLUG}/exam"):
        assert link in raw, link
    anchors = set(re.findall(r'id="(pr03-e\d\d)"', raw))
    assert anchors == {f"pr03-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr03-" not in raw  # renvois en texte : une ancre d'une autre séquence resterait masquée


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr03_course_sections()]
    assert kinds[:14] == ["theory"] * 14
    assert kinds[14:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR03"]
    assert slot.ticket == 204 and slot.title == PR03_TITLE == PRACTICAL_COURSES_BY_CODE["PR03"].title


def test_seed_publishes_pr03_in_practical_module_idempotently(db_session):
    module, uaa = _pr03(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR03_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR03").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr03_course_sections())
    assert {"PR01", "PR02", "PR03", "PR06", "PR11", "PR15", "PR16", "PR20", "PR24"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr03(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr03_specific():
    context = _pedagogical_context_for("PR03")
    assert context is get_practical_context("PR03")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    assert "une sous chaque trou" in notions and "LED polarisées" in notions and "CPU_FAN" in notions
    assert "forcer le processeur" in context.constraints and "mot-clé" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr03(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR03_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html


def test_practical_home_and_matrix_show_pr03(client, db_session):
    _pr03(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "9 cours publiés" in home
    for req in REQ:
        assert plan.requirement_status(req, {"PR03"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr03(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR03"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr03(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR03", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr03(db_session)
    for _ in range(2):  # 16 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

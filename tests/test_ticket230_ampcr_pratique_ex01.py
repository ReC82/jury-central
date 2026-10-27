"""Ticket #230 — AMPCR pratique écrite, EX01 « Examen blanc écrit — maintenance et dépannage
matériel ».

Couvre : données des dossiers **recalculées ici** indépendamment (budget et bloc
d'alimentation, verdicts de température et SMART, LED, port SATA partagé, plan lettré) ;
schémas (validité, accessibilité, fichiers statiques identiques au SVG produit) ; questions
(10 × 10 points = 100, réponses libres, au moins 3 dossiers, matière du ticket, exigences de
l'emplacement, pas de question d'acronyme) ; sujet (version candidat sans corrigé, lignes de
réponse imprimables, barème global) ; banque, seed, navigation (pas d'entraînement), sessions
d'examen (corrigé masqué avant remise, note sur 100) et absence de régression des cours PR.
Aucun appel IA réel : `FakeAIProvider` partout."""

import math
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
from app.v1.ampcr_pratique_ex01_bank import (
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
from app.v1.ampcr_pratique_ex01_course import EX01_SLUG, EX01_TITLE, ex01_course_sections
from app.v1.ampcr_pratique_ex01_figures import (
    BOARD_ANSWERS,
    BOARD_CONNECTIONS,
    BOARD_LETTERS,
    DEBUG_LEDS,
    DOSSIER_B_LOADS,
    DOSSIER_B_PSU_W,
    DOSSIER_B_TOTAL_W,
    DOSSIER_C_SMART_VERDICT,
    EX01_FIGURES,
    FREE_SATA_PORTS,
    NEW_SSD_PORT,
    STATIC_FIGURES,
    TEMP_AFTER_VERDICT,
    TEMP_FINAL_VERDICT,
    TEMP_LIMIT_C,
    TEMPERATURE_AFTER,
    TEMPERATURE_LOG,
    UEFI_STORAGE_SCREEN,
    static_svg,
)
from app.v1.ampcr_pratique_pr01_figures import BOARD_PARTS
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

SLUG = "ampcr-pratique-ex01"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _subject_raw() -> str:
    return " ".join(c for _t, c in ex01_course_sections())


def _items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in EXAM_ITEMS
    ).lower()


def _ex01(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "EX01")
    return module, uaa


# =============================================================================================
# 1. Données des dossiers, recontrôlées indépendamment
# =============================================================================================


def test_power_budget_and_psu_choice():
    total = sum(load.watts for load in DOSSIER_B_LOADS)
    assert total == DOSSIER_B_TOTAL_W == 567
    with_margin = total * 1.3  # 737,1 W
    assert math.isclose(with_margin, 737.1)
    assert DOSSIER_B_PSU_W == 750 == math.ceil(with_margin / 50) * 50
    assert DOSSIER_B_PSU_W >= 700  # recommandation du fabricant de la carte graphique
    x06 = next(i for i in EXAM_ITEMS if i.key == "X06")
    expected = " ".join(c.expected for c in x06.criteria) + " ".join(x06.correction)
    assert "567 W" in expected and "737,1 W" in expected and "750 W" in expected
    assert "310 mm" in expected and "300 mm" in expected and "DDR4" in expected


def test_temperature_and_smart_verdicts():
    # Convention des cours PR03/PR04 : anormal au maximum de la fiche, à surveiller à moins de 10 °C.
    temps = [t for _m, t, _f, _v in TEMPERATURE_LOG]
    assert TEMP_LIMIT_C == 100 and max(temps) == 100 and TEMP_FINAL_VERDICT == "anormal"
    assert [t >= 90 for t in temps] == [False, False, True, True, True]
    frequencies = [float(f.replace(",", ".")) for _m, _t, f, _v in TEMPERATURE_LOG]
    assert frequencies == sorted(frequencies, reverse=True)  # throttling
    fans = [v for *_rest, v in TEMPERATURE_LOG]
    assert max(fans) - min(fans) <= 20  # ventilateur à vitesse constante
    assert max(t for _m, t in TEMPERATURE_AFTER) < 90 and TEMP_AFTER_VERDICT == "normal"
    # Secteurs en attente et illisibles > 0 → à remplacer ; CRC à 0 → câble hors de cause.
    assert DOSSIER_C_SMART_VERDICT == "à remplacer"


def test_leds_and_shared_sata_port():
    assert [name for name, lit in DEBUG_LEDS if lit] == ["DRAM"]
    assert [name for name, _lit in DEBUG_LEDS] == ["CPU", "DRAM", "VGA", "BOOT"]
    screen = "\n".join(UEFI_STORAGE_SCREEN)
    assert f"{NEW_SSD_PORT} ..............." in screen and "Désactivé (partagé avec M.2_2)" in screen
    assert "M.2_2 (chipset) ...... SSD M.2 SATA" in screen
    for port in FREE_SATA_PORTS:
        assert f"{port} ............... Aucun" in screen


def test_lettered_board_matches_pr01_geometry():
    keys = {part.key for part, _n in BOARD_PARTS}
    letters = [letter for letter, _key in BOARD_LETTERS]
    assert letters == list("ABCDEFGHIJKL") and {key for _l, key in BOARD_LETTERS} <= keys
    assert len({key for _l, key in BOARD_LETTERS}) == 12 and set(BOARD_ANSWERS) == set(letters)
    svg = EX01_FIGURES[0].svg
    for letter, key in BOARD_LETTERS:
        assert f'data-part="{key}" data-letter="{letter}"' in svg
    assert svg.count('data-letter=""') == len(BOARD_PARTS) - 12
    by_key = {key: letter for letter, key in BOARD_LETTERS}
    assert dict(BOARD_CONNECTIONS).values() and {
        by_key["eps"], by_key["cpufan"], by_key["panel"], by_key["m21"]
    } == {letter for _what, letter in BOARD_CONNECTIONS}


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    assert len({f.key for f in EX01_FIGURES}) == len(EX01_FIGURES) == 3
    for figure in EX01_FIGURES:
        assert validate_figure(figure) == []
        html = str(render_figure(figure))
        assert 'role="img"' in html and "schéma non officiel" in html


def test_static_figure_files_are_the_generated_svg():
    for figure, path in STATIC_FIGURES:
        content = (STATIC_DIR / path).read_text()
        assert content == static_svg(figure)
        assert content.startswith("<svg ") and "xmlns=" in content and "<title>" in content


def test_schema_document_layout_points_to_static_file():
    x01 = next(i for i in EXAM_ITEMS if i.key == "X01")
    layout = _document_layout(x01.documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/ex01-plan-carte-mere.svg"
    assert len(layout["lines"]) == 13 and "non officiel" in layout["notice"]


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
        assert set(ITEM_COURSES[item.key]) <= {"PR01", "PR02", "PR03", "PR04", "PR05", "PR06"}


def test_three_dossiers_with_documents():
    for dossier in (DOSSIER_A, DOSSIER_B, DOSSIER_C):
        assert len(DOSSIER_DOCUMENTS[dossier]) >= 4
        items = [i for i in EXAM_ITEMS if ITEM_PARTS[i.key] == dossier]
        assert len(items) >= 2 and all(i.documents for i in items)
        used = {d.title for i in items for d in i.documents}
        assert used == {d.title for d in DOSSIER_DOCUMENTS[dossier]}  # chaque document sert


def test_ticket_subjects_are_all_evaluated():
    text = _items_text()
    for needle in (
        "plan", "ddr5", "bloc", "esd", "bracelet", "post", "led dram", "non détecté", "firmware",
        "température", "throttling", "ventirad", "tournevis", "démontage", "remontage", "compte rendu",
        "smart", "sauvegarde", "vérif",
    ):
        assert needle in text, needle


def test_items_cover_the_slot_requirements():
    slot = plan.EXERCISE_SLOTS_BY_CODE["EX01"]
    assert slot.ticket == 230 and slot.title == EX01_TITLE == PRACTICAL_COURSES_BY_CODE["EX01"].title
    covered = {r for i in EXAM_ITEMS for r in i.requirement_ids}
    assert set(slot.requirement_ids) <= covered
    assert covered <= set(plan.REQUIREMENTS_BY_ID)


def test_no_acronym_question_and_no_official_claim():
    for item in EXAM_ITEMS:
        prompt = item.prompt.lower()
        assert "que signifie" not in prompt and "développe" not in prompt
        assert "officiel" not in item.title.lower()
    text = _items_text()
    for wrong in ("défragmenter le ssd", "ddr4 est compatible", "adaptateur molex conseillé"):
        assert wrong not in text


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
    assert "/uaa/ampcr-pratique-ex01/exam" in text and "Ctrl + P" in text
    for code in plan.EXERCISE_SLOTS_BY_CODE["EX01"].requirement_ids:
        assert code in text


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(title) for title, _c in ex01_course_sections()]
    assert kinds == ["theory", "theory", "theory", "theory", "theory", "method", "info"]


# =============================================================================================
# 5. Banque, seed, pages, sessions
# =============================================================================================


def test_seed_publishes_ex01_after_pr06_idempotently(db_session):
    module, uaa = _ex01(db_session)
    assert uaa.slug == SLUG == EX01_SLUG and uaa.is_published and uaa.title == EX01_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="EX01").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(ex01_course_sections())
    from app.v1.parcours import listed_uaas

    codes = [u.code for u in listed_uaas(db_session.get(Module, module.id))]
    assert codes.index("EX01") == codes.index("PR06") + 1
    assert "EX01" in plan.published_uaas(db_session)
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_exam_reserve_only(db_session):
    module, uaa = _ex01(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert is_practical_exam_code("EX01") and not is_practical_exam_code("PR06")
    assert import_practical_bank(db_session, module, uaa) == 10
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert [question_usage(q) for q in questions] == ["exam"] * 10


def test_correction_context_is_ex01_specific():
    context = _pedagogical_context_for("EX01")
    assert context is get_practical_context("EX01") and context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    assert "+5 VSB" in notions and "30 %" in notions and "CPU_FAN" in notions and "SMART" in notions
    assert "/100" in context.level and "mot-clé" in context.constraints


def test_subject_page_navigation_and_home(client, db_session):
    _ex01(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    assert "Sujet" in html and f'href="/uaa/{SLUG}/practice"' not in html and f"/uaa/{SLUG}/exam" in html
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in EX01_FIGURES}
    assert html.count('class="jc-ex-question"') == 10
    assert "examen blanc EX01" in html
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus\s+· 1 examens blancs sur 6", home)  # PR07 (#207) publié ensuite
    assert client.get("/ampcr-pratique/matrice").status_code == 200
    # Les cours PR gardent leurs trois onglets.
    pr06 = client.get("/uaa/ampcr-pratique-pr06").text
    assert 'href="/uaa/ampcr-pratique-pr06/practice"' in pr06


def test_practice_redirects_to_exam(authenticated_client, db_session):
    _ex01(db_session)
    response = authenticated_client.get(f"/uaa/{SLUG}/practice", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == f"/uaa/{SLUG}/exam"
    page = authenticated_client.get(f"/uaa/{SLUG}/exam").text
    token = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
    response = authenticated_client.post(
        f"/uaa/{SLUG}/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False
    )
    assert response.status_code == 303 and response.headers["location"] == f"/uaa/{SLUG}/exam"
    assert db_session.query(QuestionnaireSession).count() == 0


def test_exam_session_hides_corrections_and_scores_on_100(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _ex01(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="EX01", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert session.question_count == 10 and fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"EX01"}
    keys = set()
    for position in range(1, 11):
        page = authenticated_client.get(f"{session_url}?q={position}").text
        assert "Corrigé de référence" not in page and "Barème" not in page
        if "ex01-plan-carte-mere.svg" in page:
            keys.add("plan")
        if "ex01-led-diagnostic.svg" in page:
            keys.add("led")
    assert keys == {"plan", "led"}  # les deux schémas sont affichés dans leurs questions
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-100" in html and "/ 100" in html and "data-score-on-20" in html


def test_pr_course_results_keep_score_on_20_only(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "ampcr-pratique-pr05", "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "data-score-on-100" not in html

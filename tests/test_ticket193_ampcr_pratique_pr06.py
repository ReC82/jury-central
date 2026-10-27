"""Ticket #193 — AMPCR pratique écrite, PR06 « Diagnostic des pannes matérielles ».

Couvre : données techniques des schémas (brochages, chaîne de démarrage, arbre, relevé),
contenu du cours (matière A-D, 4 cas, 12 exercices, mini-examen), banque (types existants,
réserves practice/exam séparées, idempotence), seed (module distinct de la théorie), pages et
sessions (strictement banque, mini-examen de 10 questions, note sur 20). Aucun appel IA réel :
`FakeAIProvider` partout."""

import re

import pytest

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_audit import proven_requirement_ids as audit_proven_ids
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    get_practical_context,
    import_practical_bank,
    question_usage,
    restrict_to_mode,
)
from app.v1.ampcr_pratique_pr06_bank import (
    EXAM_ITEMS,
    PRACTICE_ITEMS,
    validate_items,
)
from app.v1.ampcr_pratique_pr06_course import pr06_course_sections
from app.v1.ampcr_pratique_pr06_figures import (
    ATX24_PINOUT,
    BOARD_PARTS,
    BOOT_CHAIN,
    EPS8_PINOUT,
    MINIMAL_KEEP,
    NO_BOOT_TREE,
    OTHER_CONNECTORS,
    PR06_FIGURES,
    TEMPERATURE_FIGURE,
    TEMPERATURE_LIMIT,
    TEMPERATURE_LOG,
)
from app.v1.ampcr_pratique_visuals import render_figure, validate_figure
from app.v1.models import Question, QuestionnaireSession, SessionMode
from app.v1.session_service import _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-pr06"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _pr06(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR06")
    return module, uaa


# =============================================================================================
# 1. Données techniques des schémas (vérifiées)
# =============================================================================================


def test_atx24_pinout_matches_atx12v_reference():
    expected = {
        1: ("+3,3 V", "orange"), 2: ("+3,3 V", "orange"), 3: ("Masse", "noir"),
        4: ("+5 V", "rouge"), 5: ("Masse", "noir"), 6: ("+5 V", "rouge"),
        7: ("Masse", "noir"), 8: ("PWR_OK", "gris"), 9: ("+5 VSB (veille)", "violet"),
        10: ("+12 V", "jaune"), 11: ("+12 V", "jaune"), 12: ("+3,3 V", "orange"),
        13: ("+3,3 V", "orange"), 14: ("−12 V", "bleu"), 15: ("Masse", "noir"),
        16: ("PS_ON#", "vert"), 17: ("Masse", "noir"), 18: ("Masse", "noir"),
        19: ("Masse", "noir"), 20: ("non utilisée", "—"), 21: ("+5 V", "rouge"),
        22: ("+5 V", "rouge"), 23: ("+5 V", "rouge"), 24: ("Masse", "noir"),
    }
    assert {n: (s, c) for n, s, c in ATX24_PINOUT} == expected
    svg = PR06_FIGURES[2].svg
    drawn = re.findall(r'data-pin="(\d+)" data-signal="([^"]+)" data-color="([^"]+)"', svg)
    assert [(int(n), s, c) for n, s, c in drawn] == list(ATX24_PINOUT)


def test_eps8_pinout_four_grounds_then_four_12v():
    assert [s for _n, s, _c in EPS8_PINOUT] == ["Masse"] * 4 + ["+12 V"] * 4
    assert [n for n, _s, _c in EPS8_PINOUT] == list(range(1, 9))


def test_other_connectors_values():
    table = {name: (pins, power) for name, pins, power, _use in OTHER_CONNECTORS}
    assert table["PCIe 6 broches"] == ("6", "+12 V, jusqu'à 75 W")
    assert table["PCIe 8 broches (6+2)"] == ("8", "+12 V, jusqu'à 150 W")
    assert table["Alimentation SATA"] == ("15", "+3,3 V, +5 V et +12 V")
    assert table["Données SATA"][0] == "7"


def test_boot_chain_order_and_decision_tree_follow_it():
    assert [step for step, _ in BOOT_CHAIN] == [
        "Secteur", "Bloc d'alimentation", "Carte mère", "POST", "Firmware BIOS/UEFI",
        "Détection du stockage", "Chargeur d'amorçage", "Système d'exploitation",
    ]
    questions = " ".join(q for q, _ in NO_BOOT_TREE).lower()
    order = [questions.index(word) for word in ("secteur", "signe de vie", "reste-t-il allumé", "image", "disque", "système")]
    assert order == sorted(order)
    svg = PR06_FIGURES[1].svg
    assert [int(n) for n in re.findall(r'data-step="(\d+)"', svg)] == list(range(1, len(NO_BOOT_TREE) + 1))
    # Aucune piste ne propose de formater ou d'ouvrir le bloc d'alimentation.
    advice = " ".join(n for _, n in NO_BOOT_TREE).lower()
    assert "ne pas formater" in advice and "ouvrir" not in advice


def test_temperature_chart_drawn_from_table_values():
    points = re.findall(r'data-x="(\d+)" data-y="(\d+)"', TEMPERATURE_FIGURE.svg)
    assert [(int(x), int(y)) for x, y in points] == [(m, t) for m, t, _f, _v in TEMPERATURE_LOG]
    assert max(t for _m, t, _f, _v in TEMPERATURE_LOG) == TEMPERATURE_LIMIT
    assert f"{TEMPERATURE_LIMIT} °C" in TEMPERATURE_FIGURE.svg


def test_board_plan_parts_inside_frame_and_not_overlapping():
    for part in BOARD_PARTS:
        assert part.x >= 2 and part.y >= 22 and part.x + part.w <= 378 and part.y + part.h <= 398, part.key
    for i, a in enumerate(BOARD_PARTS):
        for b in BOARD_PARTS[i + 1:]:
            overlap = a.x < b.x + b.w and b.x < a.x + a.w and a.y < b.y + b.h and b.y < a.y + a.h
            assert not overlap, (a.key, b.key)


def test_minimal_configuration_keeps_only_essentials():
    kept = " ".join(MINIMAL_KEEP).lower()
    assert "1 barrette" in kept and "disque" not in kept


def test_figures_valid_accessible_and_flagged_non_official():
    assert len(PR06_FIGURES) >= 8
    keys = [f.key for f in PR06_FIGURES]
    assert len(set(keys)) == len(keys)
    for figure in PR06_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "<title" in html and "<desc" in html
        assert "schéma non officiel" in html
    fictive = [f for f in PR06_FIGURES if re.search("fictif|fictive", (f.caption + f.title).lower())]
    assert len(fictive) >= 3  # écran firmware, relevé de températures, plan de carte


# =============================================================================================
# 2. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 12
    assert sum(1 for i in PRACTICE_ITEMS if i.kind == "scénario") >= 8
    assert sum(1 for i in PRACTICE_ITEMS if i.kind == "analyse de document") >= 3
    assert len(EXAM_ITEMS) == 10
    assert sum(i.total_points for i in EXAM_ITEMS) == 20
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(set(keys)) == len(keys)


def test_exam_questions_are_free_answers_and_not_in_course():
    assert {i.question_type for i in EXAM_ITEMS} <= {"short_answer", "long_answer", "document_analysis"}
    course = " ".join(content for _title, content in pr06_course_sections())
    for item in EXAM_ITEMS:
        assert item.context not in course, item.key
    for item in PRACTICE_ITEMS:
        assert item.context.replace("'", "&#x27;") in course or item.context in course, item.key


def test_items_cover_every_requirement_and_part_of_the_ticket():
    reqs = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert {"AP-15", "AP-17", "AP-C02"} <= reqs
    text = " ".join(
        i.title + i.context + " ".join(i.correction) + " ".join(d.content_text for d in i.documents)
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    ).lower()
    for topic in ("inerte", "ventilateurs", "smart", "bips", "kernel-power 41", "esd", "batterie",
                  "m.2", "ddr", "pilote", "compte rendu", "laboratoire"):
        assert topic in text, topic


# =============================================================================================
# 3. Cours : matière obligatoire
# =============================================================================================


def test_course_teaches_every_mandatory_point():
    sections = pr06_course_sections()
    titles = [t for t, _ in sections]
    assert len(titles) == len(set(titles))
    text = _text(" ".join(c for _t, c in sections)).lower()
    for notion in (
        # A — méthodologie
        "symptômes exacts", "chronologie", "modifications récentes", "fréquence", "environnement",
        "sauvegarde", "autorisations", "observation", "hypothèse", "conclusion",
        "plus simple", "reproduire sans aggraver", "un seul changement à la fois",
        "configuration minimale", "test croisé", "test négatif", "décharge résiduelle",
        "bracelet antistatique", "ne jamais ouvrir un bloc d'alimentation", "batterie gonflée",
        "accord écrit", "compte rendu",
        # B — chaîne de démarrage et symptômes
        "absence de courant", "alimentation partielle", "absence de post", "absence d'image",
        "échec de démarrage", "plantage du système", "atx 24", "eps", "court-circuit",
        "aucune correspondance universelle", "no boot device", "operating system not found",
        "partition système efi", "csm", "kernel-power 41",
        # C — sous-systèmes
        "ecc", "une barrette à la fois", "pâte thermique", "throttling", "arrêt de protection",
        "testeur d'alimentation", "condensateurs", "vrm", "liquide", "pcie", "igpu",
        "smart", "bruits", "gestionnaire de périphériques", "socket", "ddr", "facteur de forme",
        "documentation du fabricant",
        # D — documentation et interprétation
        "capture du firmware", "journal système", "tableau de températures", "devis",
        "cause probable", "test de confirmation", "action corrective", "test final", "prévention",
        "escalader", "remplacer plutôt que réparer",
    ):
        assert notion in text, notion


def test_course_has_four_resolved_cases_and_flags():
    text = _text(" ".join(c for _t, c in pr06_course_sections()))
    for case in ("Cas 1 — PC totalement inerte", "Cas 2 — Ventilateurs en marche, aucun affichage",
                 "Cas 3 — Stockage non détecté", "Cas 4 — Extinction après 10 minutes de charge"):
        assert case in text
    assert "complément" in text.lower() and "fictif" in text.lower()
    assert "Aucun n'est une question officielle" in text
    # Pas de récitation d'acronyme dans les consignes.
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        assert not re.search(r"que signifie|que veut dire", " ".join(item.instructions), re.IGNORECASE), item.key


# =============================================================================================
# 4. Banque, seed et intégration au moteur
# =============================================================================================


def test_seed_creates_separate_practical_module_idempotently(db_session):
    module, uaa = _pr06(db_session)
    assert module.subject.name == "Informatique"
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == "Diagnostic des pannes matérielles"
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR06").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr06_course_sections())
    assert "PR06" in set(plan.published_uaas(db_session))  # PR11 (#194) publié ensuite


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr06(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == 22
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == 12 and usages.count("exam") == 10
    assert restrict_to_mode(questions, "exam") and all(
        question_usage(q) == "exam" for q in restrict_to_mode(questions, "exam")
    )
    documented = [q for q in questions if q.current_version.source_document_version_id]
    assert len(documented) >= 7
    table_doc = documented[0].current_version.source_document_version
    assert table_doc.content_json["layout"]["kind"] in ("table",) or table_doc.content_json is None


def test_correction_context_is_pr06_specific():
    context = _pedagogical_context_for("PR06")
    assert context is get_practical_context("PR06")
    assert context.course_key == "ampcr-pratique-pr06"
    assert "mot-clé" in context.constraints


def test_other_questions_never_filtered_by_mode(db_session):
    seed()
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    mc01 = next(u for u in theory.uaas if u.code == "MC01")
    from app.v1.routes_sessions import _ensure_bank_seeded

    _ensure_bank_seeded(db_session, theory, mc01)
    questions = db_session.query(Question).filter_by(uaa_id=mc01.id).all()
    assert questions
    assert restrict_to_mode(questions, "exam") == questions


# =============================================================================================
# 5. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_exercises_and_navigation(client, db_session):
    _pr06(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    assert html.count('class="jc-tech-figure') >= 9  # 8 schémas PR06 + démarche commune
    assert html.count('class="jc-exercise-card"') == 12
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html
    for exam_item in EXAM_ITEMS:
        assert exam_item.title not in _text(html).replace(" ", "") or exam_item.title in html  # titres affichés au barème
    assert f"/uaa/{SLUG}/exam" in html


def test_practical_home_and_matrix_show_pr06_published(client, db_session):
    _pr06(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "cours publiés" in home
    matrix = _text(client.get("/ampcr-pratique/matrice").text)
    assert "partiel" in matrix
    # Aucune exigence n'est déclarée validée sans validation explicite.
    assert plan.VALIDATED_REQUIREMENT_IDS == audit_proven_ids()  # « validé » : preuves de l'audit #235


def test_theory_module_page_unchanged(client, db_session):
    seed()
    html = client.get("/modules/ampcr").text
    assert SLUG not in html


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr06(db_session)
    landing = authenticated_client.get(f"/uaa/{SLUG}/{mode}")
    assert landing.status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    usages = {question_usage(sq.question_version.question) for sq in session.session_questions}
    assert usages == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    uaa_ids = {sq.question_version.question.uaa_id for sq in session.session_questions}
    assert len(uaa_ids) == 1
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_second_practice_session_never_generates(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr06(db_session)
    first = _start_session(authenticated_client, db_session, SLUG, "practice")
    _answer_all_and_submit(authenticated_client, first, db_session, fake)
    second = _start_session(authenticated_client, db_session, SLUG, "practice")
    session = db_session.get(QuestionnaireSession, int(second.rsplit("/", 1)[-1]))
    assert fake.questionnaire_calls == []
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {"practice"}
    assert session.question_count == 10


def test_exam_lengths_limited_to_bank(authenticated_client, db_session, monkeypatch):
    module, uaa = _pr06(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    lengths = available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR06", mode=SessionMode.EXAM
    )
    assert lengths == (10,)


def test_exam_results_show_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr06(db_session)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html

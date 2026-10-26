"""Ticket #197 — AMPCR pratique écrite, PR15 « Câblage RJ45 T568A/B — fabrication, schémas et tests ».

Couvre : exactitude des brochages T568A/T568B (comparés à la liste du ticket, recopiée ici
indépendamment des données du cours), paires et positions, paires séparées, liaisons droit /
croisé, schémas SVG dessinés depuis ces données (orientation, texte lisible en noir et blanc,
affichages de testeur), ordres de couleurs cités dans les corrigés, contenu du cours (matière
1-6, 4 exemples, 16 exercices, mini-examen), banque, seed, pages et sessions. Aucun appel IA
réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr15_bank import (
    E01_CORRECT,
    E01_ELEMENTS,
    E04_CASES,
    E04_CORRECT,
    E06_RESULT,
    EXAM_ITEMS,
    KIND_CHOICE,
    KIND_PINOUT,
    KIND_PROCEDURE,
    KIND_TESTER,
    PRACTICE_ITEMS,
    validate_items,
)
from app.v1.ampcr_pratique_pr15_course import PR15_TITLE, pr15_course_sections
from app.v1.ampcr_pratique_pr15_figures import (
    CHAIN_ELEMENTS,
    CHAIN_FIGURE,
    COMPARISON_FIGURE,
    CROSSOVER_FIGURE,
    CROSSOVER_LINKS,
    EXAMPLE3_FIGURE,
    EXAMPLE3_LINKS,
    PAIR_NUMBERS,
    PLUG_ORIENTATION,
    PR15_FIGURES,
    SEQUENTIAL_WRONG,
    SEQUENTIAL_WRONG_FIGURE,
    STRAIGHT_FIGURE,
    T568A_FIGURE,
    T568B_FIGURE,
    TESTER_FIGURES,
    pairs_by_position,
    split_pairs,
    wire_label,
)
from app.v1.ampcr_pratique_visuals import T568A, T568B, render_figure, validate_figure
from app.v1.models import Question, QuestionnaireSession, SessionMode
from app.v1.question_engine import validate_content
from app.v1.session_service import _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-pr15"

# Brochages recopiés du cahier des charges du ticket #197 (§ 2), indépendamment du code.
TICKET_T568B = "1 blanc/orange, 2 orange, 3 blanc/vert, 4 bleu, 5 blanc/bleu, 6 vert, 7 blanc/marron, 8 marron"
TICKET_T568A = "1 blanc/vert, 2 vert, 3 blanc/orange, 4 bleu, 5 blanc/bleu, 6 orange, 7 blanc/marron, 8 marron"


def _parse(order: str) -> tuple[str, ...]:
    return tuple(part.split(" ", 1)[1].replace("/", "-") for part in order.split(", "))


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_text() -> str:
    return _text(" ".join(c for _t, c in pr15_course_sections())).lower()


def _pr15(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR15")
    return module, uaa


def _svg_pins(svg: str) -> list[tuple[int, str]]:
    return [(int(p), w) for p, w in re.findall(r'data-pin="(\d)" data-wire="([a-z-]+)"', svg)]


def _svg_links(svg: str) -> set[str]:
    return set(re.findall(r'data-link="([0-9a-z-]+)"', svg))


# =============================================================================================
# 1. Brochages et paires : données vérifiées
# =============================================================================================


def test_pinouts_match_the_ticket_and_tia_568():
    assert _parse(TICKET_T568B) == T568B
    assert _parse(TICKET_T568A) == T568A
    differing = [i for i, (a, b) in enumerate(zip(T568A, T568B, strict=True), start=1) if a != b]
    assert differing == [1, 2, 3, 6]  # A et B échangent orange et vert ; bleu et marron identiques


def test_pairs_and_positions():
    assert pairs_by_position(T568B) == {(1, 2): "orange", (3, 6): "vert", (4, 5): "bleu", (7, 8): "marron"}
    assert pairs_by_position(T568A) == {(1, 2): "vert", (3, 6): "orange", (4, 5): "bleu", (7, 8): "marron"}
    assert PAIR_NUMBERS == {"bleu": 1, "orange": 2, "vert": 3, "marron": 4}
    for wires in (T568A, T568B):
        assert sorted(wires) == sorted(SEQUENTIAL_WRONG)  # mêmes 8 fils, chacun une fois
        assert split_pairs(wires) == []
    assert split_pairs(SEQUENTIAL_WRONG) == [(3, 6), (4, 5)]
    with pytest.raises(ValueError):
        pairs_by_position(SEQUENTIAL_WRONG)


def test_straight_and_crossover_links():
    assert CROSSOVER_LINKS == ((1, 3), (2, 6), (3, 1), (4, 4), (5, 5), (6, 2), (7, 7), (8, 8))
    assert {f"{a}-{b}" for a, b in CROSSOVER_LINKS} == _svg_links(CROSSOVER_FIGURE.svg)
    assert _svg_links(STRAIGHT_FIGURE.svg) == {f"{p}-{p}" for p in range(1, 9)}
    # Exemple 3 : vert et bleu permutés à un bout → 4↔6.
    assert EXAMPLE3_LINKS == ((1, 1), (2, 2), (3, 3), (4, 6), (5, 5), (6, 4), (7, 7), (8, 8))
    assert {"4-6", "6-4"} <= _svg_links(EXAMPLE3_FIGURE.svg)


# =============================================================================================
# 2. Schémas : dessinés depuis les données, orientés, lisibles en noir et blanc
# =============================================================================================


@pytest.mark.parametrize(("figure", "wires"), [(T568A_FIGURE, T568A), (T568B_FIGURE, T568B), (SEQUENTIAL_WRONG_FIGURE, SEQUENTIAL_WRONG)])
def test_pinout_figures_drawn_from_data_in_reading_order(figure, wires):
    assert _svg_pins(figure.svg) == list(enumerate(wires, start=1))
    text = _text(figure.svg)
    for pin, wire in enumerate(wires, start=1):
        assert f"{pin} {wire_label(wire)} paire" in text  # chaque broche écrite en toutes lettres (N&B)
    assert "broche 1 à gauche" in PLUG_ORIENTATION and PLUG_ORIENTATION in figure.alt
    assert "broche 1 à gauche" in figure.caption.lower() or figure is SEQUENTIAL_WRONG_FIGURE


def test_wrong_order_figure_is_flagged_as_wrong():
    assert "ORDRE FAUX" in SEQUENTIAL_WRONG_FIGURE.svg and "FAUX" in SEQUENTIAL_WRONG_FIGURE.caption


def test_comparison_figure_rows_match_both_standards():
    rows = re.findall(r'data-pin="(\d)" data-a="([a-z-]+)" data-b="([a-z-]+)"', COMPARISON_FIGURE.svg)
    assert [(int(p), a, b) for p, a, b in rows] == [(i, a, b) for i, (a, b) in enumerate(zip(T568A, T568B, strict=True), start=1)]
    assert COMPARISON_FIGURE.svg.count(">≠<") == 4 and COMPARISON_FIGURE.svg.count(">=<") == 4


def test_tester_figures_show_the_four_required_results():
    good, opened, reversed_, split = TESTER_FIGURES
    assert _svg_links(good.svg) == {f"{p}-{p}" for p in range(1, 9)}
    assert "7-ouvert" in _svg_links(opened.svg) and "7-7" not in _svg_links(opened.svg)
    assert {"1-2", "2-1"} <= _svg_links(reversed_.svg)
    assert _svg_links(split.svg) == {f"{p}-{p}" for p in range(1, 9)}  # continuité parfaite…
    assert set(re.findall(r'data-split="([0-9-]+)"', split.svg)) == {"3-6", "4-5"}  # …mais paires séparées
    for figure in TESTER_FIGURES:
        assert "fictif" in (figure.caption + figure.svg).lower()
        assert "RÉSULTAT" in figure.svg


def test_chain_figure_and_lengths():
    assert CHAIN_ELEMENTS[0][0] == "Switch (baie)" and CHAIN_ELEMENTS[-1][0] == "PC"
    assert set(re.findall(r'data-bracket="([0-9-]+)"', CHAIN_FIGURE.svg)) == {"3-5", "1-7"}
    assert "90 m" in CHAIN_FIGURE.svg and "100 m" in CHAIN_FIGURE.svg
    assert all(len(detail) <= 34 for _n, detail in CHAIN_ELEMENTS)  # une ligne, rien de tronqué


def test_figures_valid_accessible_and_unique():
    assert len(PR15_FIGURES) >= 13
    keys = [f.key for f in PR15_FIGURES]
    assert len(set(keys)) == len(keys)
    for figure in PR15_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "<title" in html and "<desc" in html and "schéma non officiel" in html


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 15
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_PINOUT) >= 5
    assert kinds.count(KIND_TESTER) >= 4
    assert kinds.count(KIND_CHOICE) >= 3
    assert kinds.count(KIND_PROCEDURE) >= 3
    assert len(EXAM_ITEMS) == 10 and sum(i.total_points for i in EXAM_ITEMS) == 20
    assert {i.question_type for i in EXAM_ITEMS} <= {"short_answer", "long_answer", "document_analysis"}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(set(keys)) == len(keys)


def test_auto_corrected_answers_are_technically_right():
    for element, index in zip(E01_ELEMENTS, E01_CORRECT, strict=True):
        assert T568B[index] == element
    labels = ("T568A seulement", "T568B seulement", "T568A et T568B")
    for (pin, wire), index in zip(E04_CASES, E04_CORRECT, strict=True):
        in_a, in_b = T568A[pin - 1] == wire, T568B[pin - 1] == wire
        assert in_a or in_b
        assert labels[index] == ("T568A et T568B" if in_a and in_b else "T568A seulement" if in_a else "T568B seulement")
    # Fiche tenue languette vers soi : ordre exactement inversé.
    assert E06_RESULT[0] == "marron" and E06_RESULT[7] == "blanc-orange"


def test_every_colour_order_quoted_in_corrections_is_a_known_one():
    """Tout ordre « 1 x, 2 y, … 8 z » cité dans un corrigé, un barème ou le cours est T568A,
    T568B, l'ordre faux de l'exercice E03/X04 ou l'ordre inversé de E06 : jamais un brochage
    inventé ou mal recopié."""
    known = {T568A, T568B, SEQUENTIAL_WRONG, E06_RESULT}
    pattern = re.compile(r"1 ([a-z/]+), 2 ([a-z/]+), 3 ([a-z/]+), 4 ([a-z/]+), 5 ([a-z/]+), 6 ([a-z/]+), 7 ([a-z/]+),? (?:et )?8 ([a-z/]+)")
    texts = [" ".join((*i.correction, *(c.expected for c in i.criteria), i.context)) for i in PRACTICE_ITEMS + EXAM_ITEMS]
    texts += [_text(c) for _t, c in pr15_course_sections()]
    found = 0
    for text in texts:
        for match in pattern.finditer(text):
            assert tuple(w.replace("/", "-") for w in match.groups()) in known, match.group(0)
            found += 1
    assert found >= 15


def test_no_acronym_question_and_full_context():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.title, item.context, *item.instructions))
        assert not re.search(r"que signifie|que veut dire|développe[rz]? l'acronyme", text, re.IGNORECASE), item.key
        assert len(item.context) >= 150, item.key


def test_items_content_matches_existing_question_types():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        content = item_content(item, [1, 2][: len(item.documents)])
        validate_content(item.question_type, 1, content)
    ordering = [i for i in PRACTICE_ITEMS if i.question_type == "ordering"]
    assert ordering
    for item in ordering:
        content = item_content(item, [])
        assert content["correct_order"] != [x["id"] for x in content["items"]]


def test_four_examples_and_exam_not_in_course():
    text = _text(" ".join(c for _t, c in pr15_course_sections()))
    for example in ("Exemple 1 — Fabriquer un câble droit B-B", "Exemple 2 — Fabriquer un câble croisé A-B",
                    "Exemple 3 — Diagnostiquer une erreur sur les broches 3/6",
                    "Exemple 4 — Expliquer un lien limité à 100 Mb/s"):
        assert example in text, example
    course = " ".join(content for _title, content in pr15_course_sections())
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_no_unqualified_cat6_10g_100m_claim():
    everything = _course_text() + " ".join(
        " ".join((*i.correction, *(c.expected for c in i.criteria))) for i in PRACTICE_ITEMS + EXAM_ITEMS
    ).lower()
    for match in re.finditer(r"10 gb/s sur 100 m", everything):
        before = everything[max(0, match.start() - 60): match.start()]
        assert "cat6a" in before or "jamais" in before or "affirmer" in before, before


# =============================================================================================
# 4. Cours : toute la matière obligatoire (sections 1 à 6 du ticket)
# =============================================================================================


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr15_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # 1 — supports et connecteurs
        "4 paires torsadées", "8 conducteurs", "rôle de la torsade", "détorsadage excessif", "u/utp", "f/utp",
        "u/ftp", "s/ftp", "utp", "ftp", "stp", "blindage", "continuité de bout en bout", "mise à la terre", "cat5e",
        "cat6a", "fréquence", "débit", "compatibilité", "8p8c", "communément appelée rj45", "prise", "fiche",
        "keystone", "panneau de brassage", "cordon", "monobrin", "multibrin", "rayon de courbure", "écrasement",
        "traction", "humidité", "secteur", "cheminement",
        # 2 — brochage
        "broche 1 à gauche", "échangent la paire orange et la paire verte", "1-2", "3-6", "4-5", "7-8",
        "paire séparée", "split pair",
        # 3 — droit / croisé
        "câble droit", "câble croisé", "auto mdi-x", "pc ↔ switch", "switch ↔ switch", "pc ↔ pc", "10/100",
        "1000base-t", "quatre paires", "deux sens", "négociation", "configuration ip",
        # 4 — fabrication
        "coupe propre", "sans entailler", "au plus près de la fiche", "butée", "gaine", "sertir",
        "avant toute mise en service", "pince à sertir", "dénudeur", "coupe-câble", "wiremap", "qualification",
        "certification", "poinçonnage", "terminer un câble permanent",
        # 5 — tests et dépannage
        "circuit ouvert", "court-circuit", "fils inversés", "paires croisées", "intermittent", "mauvais contact",
        "ni la catégorie, ni le débit, ni l'absence de diaphonie", "lien absent", "100 mb/s au lieu de 1 gb/s",
        "instabilité", "erreur de brochage", "pilote", "longueur", "connecteur non adapt", "100 m", "90 m",
        "atténuation", "next", "rapport signal/bruit",
        # 6 — contexte professionnel
        "baie", "prise murale", "étiquet", "préfabriqué", "besoin", "norme choisie", "schéma", "outils",
        "tests avant", "tests après", "défauts corrigés", "validation",
    ):
        assert notion in text, notion


def test_course_flags_requirements_complements_and_fictive_supports():
    text = _text(" ".join(c for _t, c in pr15_course_sections()))
    for req in ("AP-34", "AP-18", "AP-20", "AP-C01"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr15_course_sections()]
    assert kinds.count("exam") == 1 and kinds.count("exercise") == 1 and kinds.count("example") == 1
    assert kinds[-1] == "info" and "summary" in kinds and "warning" in kinds


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_seed_publishes_pr15_in_practical_module_idempotently(db_session):
    module, uaa = _pr15(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR15_TITLE
    assert PRACTICAL_COURSES_BY_CODE["PR15"].title == plan.COURSE_SLOTS_BY_CODE["PR15"].title == PR15_TITLE
    assert plan.COURSE_SLOTS_BY_CODE["PR15"].ticket == 197
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR15").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr15_course_sections())
    assert {"PR06", "PR11", "PR15"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr15(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10
    layouts = [
        (q.current_version.source_document_version.content_json or {}).get("layout", {}).get("kind")
        for q in questions if q.current_version.source_document_version_id
    ]
    assert "console" in layouts and "table" in layouts


def test_correction_context_is_pr15_specific():
    context = _pedagogical_context_for("PR15")
    assert context is get_practical_context("PR15")
    assert context.course_key == "ampcr-pratique-pr15"
    notions = " ".join(context.allowed_notions)
    assert TICKET_T568B in notions and TICKET_T568A in notions
    assert "Cat6 = 10 Gb/s sur 100 m" in context.constraints and "mot-clé" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr15(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR15_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html


def test_practical_home_and_matrix_show_pr15(client, db_session):
    _pr15(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "3 cours publiés" in home
    matrix = _text(client.get("/ampcr-pratique/matrice").text)
    assert "partiel" in matrix
    assert plan.requirement_status("AP-34", {"PR15"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr15(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR15"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr15(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR15", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr15(db_session)
    for _ in range(2):  # 16 exercices : deux sessions couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

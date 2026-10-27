"""Ticket #216 — AMPCR pratique écrite, PR13 « Câbles UTP, FTP, STP et coaxial — choix et pose ».

Couvre : données de référence **recontrôlées ici** indépendamment (désignation X/YTP et
construction, noms historiques, règle de choix, rayon de courbure, traction, distances
EN 50174-2, longueurs du canal, repères) ; schémas SVG (validité, accessibilité, données
dessinées) ; exercices et mini-examen (format du socle, remises en ordre et classements
auto-corrigés, pas de question d'acronyme, contexte complet) ; cours (matière du ticket, 2
procédures, 5 cas résolus, affirmations techniques justes, supports fictifs, cartes) ; banque,
seed, pages et sessions. Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr13_bank import (
    E10_BAD,
    E12_MIN,
    E14_BAD,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_CHOICE,
    KIND_COAX,
    KIND_ERROR,
    KIND_ORDER,
    KIND_POSE,
    KIND_STRUCTURE,
    PRACTICE_ITEMS,
    REQ,
    X06_MIN,
    X07_MIN,
    X08_ERRORS,
    validate_items,
)
from app.v1.ampcr_pratique_pr13_course import CASES, PR13_SLUG, PR13_TITLE, pr13_course_sections
from app.v1.ampcr_pratique_pr13_figures import (
    BEND_EXAMPLES,
    CHAIN_ELEMENTS,
    CHOICE_STEPS,
    CHOICE_TREE,
    EMI_HIGH,
    EMI_LOW,
    EMI_MEDIUM,
    ERR_BEND,
    ERR_PULL,
    ERR_SEPARATION,
    FAMILY_COAX50,
    FAMILY_COAX75,
    FAMILY_FIBRE,
    FAMILY_FUTP,
    FAMILY_SFTP,
    FAMILY_UUTP,
    POSE_STEPS,
    PR13_FIGURES,
    PROCEDURES,
    SECTION_DESIGNATIONS,
    SEPARATION_MM,
    SERVICE_10BASE2,
    SERVICE_TV,
    SERVICE_VIDEO,
    STRUCT_BOTH,
    STRUCT_NONE,
    STRUCT_OVERALL,
    STRUCT_PAIR,
    Need,
    Run,
    category_for,
    channel_errors,
    choose,
    label_for,
    min_bend_radius_mm,
    min_separation_mm,
    parse_designation,
    run_errors,
    structure_of,
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

SLUG = "ampcr-pratique-pr13"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr13_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr13(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR13")
    return module, uaa


# =============================================================================================
# 1. Données de référence, recontrôlées indépendamment
# =============================================================================================


def test_designation_x_ytp_and_structures():
    # ISO/IEC 11801 : lettre avant la barre = écran global, lettre(s) avant TP = écran de paire.
    expected = {
        "U/UTP": (("U", "U"), STRUCT_NONE),
        "F/UTP": (("F", "U"), STRUCT_OVERALL),
        "U/FTP": (("U", "F"), STRUCT_PAIR),
        "S/FTP": (("S", "F"), STRUCT_BOTH),
        "SF/UTP": (("SF", "U"), STRUCT_OVERALL),
        "S/UTP": (("S", "U"), STRUCT_OVERALL),
        "F/FTP": (("F", "F"), STRUCT_BOTH),
    }
    for designation, (parsed, structure) in expected.items():
        assert parse_designation(designation) == parsed, designation
        assert structure_of(designation) == structure, designation
    for bad in ("UTP", "FTP", "X/UTP", "U/XTP", "U/UTQ"):
        with pytest.raises(ValueError):
            parse_designation(bad)
    assert SECTION_DESIGNATIONS == ("U/UTP", "F/UTP", "U/FTP", "S/FTP")


def test_choice_rule():
    assert category_for(1) == "Cat5e" and category_for(10) == "Cat6A"
    assert choose(Need(emi=EMI_LOW)).family == FAMILY_UUTP
    assert choose(Need(emi=EMI_MEDIUM, grounded=True)).family == FAMILY_FUTP
    assert choose(Need(emi=EMI_MEDIUM, grounded=False)).family == FAMILY_UUTP  # écran sans terre inutile
    assert choose(Need(emi=EMI_HIGH, grounded=True)).family == FAMILY_SFTP
    assert choose(Need(emi=EMI_HIGH, grounded=False)).family == FAMILY_FIBRE
    assert choose(Need(length_m=101)).family == FAMILY_FIBRE  # canal ≤ 100 m
    assert choose(Need(length_m=100)).family == FAMILY_UUTP
    assert choose(Need(rate_gbps=10, emi=EMI_HIGH)).cable == "Cat6A S/FTP"
    assert choose(Need(service=SERVICE_VIDEO)).family == FAMILY_COAX75
    assert "BNC 75" in choose(Need(service=SERVICE_VIDEO)).connector
    assert choose(Need(service=SERVICE_TV)).connector == "Fiches F"
    assert choose(Need(service=SERVICE_10BASE2, length_m=50)).family == FAMILY_COAX50
    with pytest.raises(ValueError):
        choose(Need(service=SERVICE_10BASE2, length_m=200))  # segment 10BASE2 ≤ 185 m


def test_pose_rules_values():
    # TIA-568 : 4 × Ø non écranté, 8 × Ø écranté ; coaxial : convention du cours 10 × Ø.
    assert min_bend_radius_mm(6, "U/UTP") == 24
    assert min_bend_radius_mm(7.5, "S/FTP") == 60
    assert min_bend_radius_mm(7, "U/FTP") == 56  # un écran par paire suffit à être « écranté »
    assert min_bend_radius_mm(6.1, None) == 61
    assert E12_MIN == pytest.approx(62.4) and X07_MIN == pytest.approx(60.8)
    # EN 50174-2, sans cloison, jusqu'à 3 circuits.
    assert SEPARATION_MM == {"a": 300, "b": 100, "c": 50, "d": 10}
    assert min_separation_mm(None) == 300 == X06_MIN
    base = {"name": "T", "designation": "U/UTP", "diameter_mm": 6, "bend_radius_mm": 30, "pull_n": 80}
    assert run_errors(Run(**base, power_distance_mm=None)) == []
    assert run_errors(Run(**{**base, "bend_radius_mm": 20}, power_distance_mm=None)) == [ERR_BEND]
    assert run_errors(Run(**{**base, "pull_n": 111}, power_distance_mm=None)) == [ERR_PULL]
    assert run_errors(Run(**base, power_distance_mm=99, separation_class="b")) == [ERR_SEPARATION]
    assert run_errors(Run(**base, power_distance_mm=100, separation_class="b")) == []
    assert run_errors(Run(**base, power_distance_mm=5, metal_divider=True)) == []


def test_lengths_and_labels():
    assert channel_errors(90, 10) == []
    assert channel_errors(93, 3) == ["lien permanent de 93 m > 90 m"]  # canal 96 m mais lien > 90
    assert channel_errors(85, 12) == ["cordons de 12 m au total > 10 m"]
    assert len(channel_errors(89, 12)) == 2
    assert X08_ERRORS == ["lien permanent de 92 m > 90 m"]
    assert E10_BAD == ("B1-P1-03", "B1-P1-04", "B1-P1-05")
    assert label_for(1, 1, 7) == "B1-P1-07"
    assert E14_BAD == ("Bureau 2, prise droite", "Bureau 3", "Imprimante du couloir")


def test_procedures_order():
    assert [label for label, _d in POSE_STEPS] == ["Préparer", "Étiqueter", "Tirer", "Fixer", "Raccorder", "Tester et consigner"]
    assert [label for label, _d in CHOICE_STEPS] == ["Besoin", "Longueur", "Environnement", "Catégorie", "Blindage", "Consigner"]
    assert CHAIN_ELEMENTS[0][0] == "Switch (baie)" and CHAIN_ELEMENTS[-1][0] == "PC"
    assert len(PROCEDURES) == 2


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    keys = [f.key for f in PR13_FIGURES]
    assert len(keys) == len(set(keys)) == 9  # ticket : au moins 4 schémas ou documents
    for figure in PR13_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR13_FIGURES}
    sections = by_key["pr13-coupes-paires"].svg
    for designation in SECTION_DESIGNATIONS:
        overall, pair = parse_designation(designation)
        assert f'data-designation="{designation}" data-overall="{overall}" data-pair="{pair}"' in sections
    # Écrans par paire : U/FTP et S/FTP → 2 × 4 ; feuille globale : F/UTP ; tresse globale : S/FTP.
    assert sections.count('data-pair-screen="F"') == 8
    assert sections.count("data-overall-foil") == 1 and sections.count("data-overall-braid") == 1
    for key, steps in (("pr13-procedure-pose", POSE_STEPS), ("pr13-procedure-choix", CHOICE_STEPS)):
        for index, (label, _detail) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in by_key[key].svg, (key, label)
    assert by_key["pr13-arbre-choix"].svg.count("data-step=") == len(CHOICE_TREE)
    bars = re.findall(r'data-class="(\w)" data-mm="(\d+)"', by_key["pr13-separation-energie"].svg)
    assert [(c, int(mm)) for c, mm in bars] == list(SEPARATION_MM.items())
    radii = re.findall(r'data-radius="([\d,]+)"', by_key["pr13-rayon-courbure"].svg)
    assert radii == [f"{min_bend_radius_mm(d, des):g}".replace(".", ",") for _n, des, d in BEND_EXAMPLES]
    screen = by_key["pr13-continuite-ecran"].svg
    assert "✓" in screen and "✗" in screen
    chain = by_key["pr13-chaine-baie-prise"].svg
    assert chain.count("data-element=") == len(CHAIN_ELEMENTS) and 'data-bracket="3-5"' in chain


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 16 and len(EXAM_ITEMS) == 10  # ticket : ≥ 16 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    for kind, minimum in ((KIND_ORDER, 3), (KIND_STRUCTURE, 3), (KIND_CHOICE, 2), (KIND_POSE, 3),
                          (KIND_COAX, 2), (KIND_ERROR, 2)):
        assert kinds.count(kind) >= minimum, kind
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert REQ <= covered
    assert set(plan.COURSE_SLOTS_BY_CODE["PR13"].requirement_ids) == REQ
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 5
    assert sum(1 for i in PRACTICE_ITEMS if i.documents) >= 5  # marquage, longueurs, écran, fiche, étiquettes
    # Ticket : sélection selon contraintes évaluée à l'examen aussi.
    assert sum(1 for i in EXAM_ITEMS if i.kind == KIND_CHOICE) >= 3


def test_auto_corrected_answers():
    by_key = {i.key: i for i in PRACTICE_ITEMS}

    def ordered(key: str) -> list[str]:
        o = by_key[key].ordering
        return [o.steps[i].split(" — ")[0] for i in o.correct]

    assert ordered("E01") == [label for label, _d in POSE_STEPS]
    assert ordered("E02") == [label for label, _d in CHOICE_STEPS]
    assert ordered("E03") == [name for name, _d in CHAIN_ELEMENTS]

    def answers(key: str) -> dict[str, str]:
        c = by_key[key].classification
        return dict(zip(c.elements, (c.categories[i] for i in c.correct), strict=True))

    e04 = answers("E04")
    assert e04["Câble marqué « U/FTP »"] == STRUCT_PAIR and e04["Câble marqué « F/UTP »"] == STRUCT_OVERALL
    assert e04["Câble marqué « S/FTP »"] == STRUCT_BOTH and e04["Câble marqué « U/UTP »"] == STRUCT_NONE
    e05 = answers("E05")
    assert next(v for k, v in e05.items() if "avocats" in k) == FAMILY_UUTP
    assert next(v for k, v in e05.items() if "soudure" in k) == FAMILY_SFTP
    assert next(v for k, v in e05.items() if "140 m" in k) == FAMILY_FIBRE
    assert next(v for k, v in e05.items() if "Caméra" in k) == FAMILY_COAX75
    assert next(v for k, v in e05.items() if "10BASE2" in k) == FAMILY_COAX50
    assert next(v for k, v in e05.items() if "ascenseur" in k) == FAMILY_FUTP
    assert next(v for k, v in e05.items() if "Entrepôt" in k) == FAMILY_UUTP
    assert next(v for k, v in e05.items() if "Hall" in k) == FAMILY_FIBRE
    e06 = answers("E06")
    assert next(v for k, v in e06.items() if "S/FTP Ø 7,5" in k) == ERR_BEND
    assert next(v for k, v in e06.items() if "180 N" in k) == ERR_PULL
    assert next(v for k, v in e06.items() if "classe inconnue" in k) == ERR_SEPARATION
    assert next(v for k, v in e06.items() if "cloison métallique" in k) == "Conforme"
    e07 = answers("E07")
    assert next(v for k, v in e07.items() if "imprimante" in k).startswith("Multibrin")
    assert next(v for k, v in e07.items() if "deux baies" in k).startswith("Monobrin")
    e08 = answers("E08")
    assert next(v for k, v in e08.items() if "10BASE2 en RG-58" in k) == "50 Ω"
    assert next(v for k, v in e08.items() if "SDI" in k) == "75 Ω"
    assert next(v for k, v in e08.items() if "Parabole" in k) == "75 Ω"
    for item in PRACTICE_ITEMS:  # aucune remise en ordre déjà dans l'ordre attendu, aucun classement trivial
        if item.ordering:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key
        if item.classification:
            assert list(item.classification.correct) != list(range(len(item.classification.elements))), item.key
            assert len(set(item.classification.correct)) > 1, item.key


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("4 paires", "8 conducteurs", "différentiel", "diaphonie", "atténuation", "13 mm",
                  "x = protection globale", "u/utp", "f/utp", "u/ftp", "s/ftp", "iso/iec 11801",
                  "continu", "barrette de terre", "360°", "cat5e", "cat6a", "500 mhz", "monobrin", "multibrin",
                  "8p8c", "keystone", "panneau de brassage", "âme", "diélectrique", "tresse", "gaine",
                  "50 ω", "75 ω", "rg-58", "rg-59", "10base2", "185 m", "en 50174-2", "300 mm", "angle droit",
                  "4 × son diamètre", "110 n", "jamais d'agrafe", "90 m", "100 m", "même repère aux deux",
                  "continuité de l'écran", "fiche technique", "fibre optique"):
        assert right in text, right
    for wrong in ("cat6 = 6 gb/s est juste", "le s/ftp n'a pas besoin de terre", "u/ftp n'a aucun écran",
                  "mélanger 50 et 75 ω est sans effet", "agrafer le câble", "200 m en cat6a",
                  "le monobrin convient aux cordons", "rg-58 est un câble 75"):
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
    families = {choose(need).family for _t, _s, need in CASES}
    assert families == {FAMILY_UUTP, FAMILY_SFTP, FAMILY_FIBRE, FAMILY_COAX75}
    for title, _s, need in CASES:
        assert title in text and choose(need).cable in text, title
    assert text.count("Conclusion rédigée.") == 5
    for i in (1, 2):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr13_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "4 paires torsadées", "rôle de la torsade", "diaphonie", "perturbations électromagnétiques",
        "atténuation", "débit", "catégorie",
        "u/utp", "f/utp", "u/ftp", "s/ftp", "noms historiques", "utp", "ftp", "stp",
        "blindage", "continuité", "mise à la terre", "selon le système",
        "5e", "cat6", "6a", "rigide", "souple", "8p8c", "prise", "cordon", "baie",
        "âme", "diélectrique", "tresse", "gaine", "50 ω", "75 ω", "10base2", "vidéo",
        "séparation", "courbure", "traction", "longueurs", "repérage", "test",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-18", "AP-20"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "conventions du cours" in text.lower()
    for link in ("/uaa/ampcr-mc15", "/uaa/ampcr-pratique-pr15", "/uaa/ampcr-pratique-pr16",
                 f"/uaa/{PR13_SLUG}/practice", f"/uaa/{PR13_SLUG}/exam"):
        assert link in raw, link
    # PR14 et PR17 ne sont pas encore publiés : renvoi en texte seulement.
    for code in ("PR14", "PR17"):
        assert f"/uaa/ampcr-pratique-{code.lower()}" not in raw and code in raw
    anchors = set(re.findall(r'id="(pr13-e\d\d)"', raw))
    assert anchors == {f"pr13-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr13-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr13_course_sections()]
    assert kinds[:10] == ["theory"] * 10
    assert kinds[10:] == ["example", "warning", "exercise", "exam", "summary", "info"]


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR13"]
    assert slot.ticket == 216 and slot.title == PR13_TITLE == PRACTICAL_COURSES_BY_CODE["PR13"].title


def test_seed_publishes_pr13_in_practical_module_idempotently(db_session):
    module, uaa = _pr13(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR13_TITLE and uaa.position == 13
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR13").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr13_course_sections())
    assert {"PR12", "PR13", "PR15", "PR16"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR12") < ordered.index("EX02") < ordered.index("PR13") < ordered.index("PR15")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr13(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr13_specific():
    context = _pedagogical_context_for("PR13")
    assert context is get_practical_context("PR13")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("X/YTP", "S/FTP", "relié à la terre", "Cat6A 500 MHz", "monobrin (/1)", "RG-59",
                   "classe a 300 mm", "8 × Ø écranté", "≤ 110 N", "lien permanent ≤ 90 m", "B1-P1-07"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "mélange de 50 et 75 Ω" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr13(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR13_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and "jc-pr-console" in html


def test_practical_home_and_matrix_show_pr13(client, db_session):
    _pr13(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR14 (#217) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR13"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr13(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR13"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr13(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR13", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr13(db_session)
    for _ in range(2):  # 17 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

"""Ticket #227 — AMPCR pratique écrite, PR28 « Outillage, sécurité et protection des données ».

Couvre : règles du cours **recontrôlées ici** indépendamment (inventaire et outil propre à chaque
tâche, kits, risques, débranchement, tolérances du bloc, règle 3-2-1, empreintes SHA-256,
prérequis avant effacement, filières de fin de vie, arbre d'incident) ; cinq interventions
résolues (valeurs calculées) ; schémas SVG (validité, accessibilité, données dessinées, schémas à
compléter sans leurs réponses, fichiers statiques) ; exercices et mini-examen (format du socle,
auto-correction, valeurs des corrigés) ; cours (matière du ticket, liens, supports fictifs,
cartes) ; banque, seed, pages et sessions. Aucun appel IA réel : `FakeAIProvider` partout."""

import hashlib
import re
from html import escape
from pathlib import Path

import pytest

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    _document_layout,
    get_practical_context,
    import_practical_bank,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_pr02_figures import RAILS, within_tolerance
from app.v1.ampcr_pratique_pr27_figures import walk
from app.v1.ampcr_pratique_pr28_bank import (
    E06_MEASURED,
    E11_PLANS,
    E12_COPY,
    E12_SOURCE,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_DATA,
    KIND_ORDER,
    KIND_SCHEMA,
    KIND_TOOL,
    KIND_TREE,
    KIND_WRITE,
    PRACTICE_ITEMS,
    REQ,
    X02_MEASURED,
    X05_COPIES,
    validate_items,
)
from app.v1.ampcr_pratique_pr28_course import PR28_SLUG, PR28_TITLE, pr28_course_sections
from app.v1.ampcr_pratique_pr28_figures import (
    C3_321_AFTER,
    C3_321_BEFORE,
    C3_INTEGRITY,
    C3_MISSING,
    C5_HDD_OK,
    C5_ROUTES,
    C5_SSD_FORMAT_OK,
    CASES,
    DISCONNECT_STEPS,
    ESD_PARTS,
    INCIDENT_BLANK_ANSWERS,
    INCIDENT_TREE,
    INTERVENTIONS,
    MISS_1,
    MISS_2,
    MISS_3,
    OP_ERASE,
    OP_REINSTALL,
    PR28_FIGURES,
    PRE_AUTHORIZED,
    PRE_BACKUP,
    PRE_CONSENT,
    PRE_KEY,
    PRE_LICENSES,
    RISKS,
    ROUTE_BATTERY,
    ROUTE_DATA,
    ROUTE_EEE,
    STATIC_FIGURES,
    SUP_CLOUD,
    SUP_EXTERNAL,
    SUP_INTERNAL,
    SUP_NAS,
    SUP_USB_KEY,
    TASKS,
    TOOLS,
    TOOLS_BY_KEY,
    W_BATTERY,
    W_DATA,
    W_EEE,
    Copy,
    check_321,
    compare_copy,
    fingerprint,
    kit,
    missing_prerequisites,
    required_prerequisites,
    static_svg,
    waste_route,
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

SLUG = "ampcr-pratique-pr28"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr28_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").replace("&#x27;", "'").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _item(key: str):
    return next(i for i in PRACTICE_ITEMS + EXAM_ITEMS if i.key == key)


def _pr28(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR28")
    return module, uaa


# =============================================================================================
# 1. Règles du cours, recontrôlées indépendamment
# =============================================================================================


def test_inventory_covers_ticket_tools_and_each_task_has_one_tool():
    names = " ".join(t.name.lower() for t in TOOLS)
    for tool in ("tournevis", "pince", "bracelet", "tapis", "testeur d'alimentation", "multimètre",
                 "pâte thermique", "air sec", "sertisseuse 8p8c", "dénudeur", "punch-down", "wiremap", "bnc",
                 "fibre", "laser"):
        assert tool in names, tool
    assert len({t.key for t in TOOLS}) == len(TOOLS)
    assert len({task for task, _k in TASKS}) == len(TASKS) and len({k for _t, k in TASKS}) == len(TASKS)
    assert all(t.precaution and t.use for t in TOOLS)
    assert "jamais ouvert" in TOOLS_BY_KEY["testeur-alim"].precaution
    assert "230 V" in TOOLS_BY_KEY["multimetre"].precaution and "hors tension" in TOOLS_BY_KEY["multimetre"].precaution
    assert "PoE" in TOOLS_BY_KEY["wiremap"].precaution
    assert "selon la procédure" in TOOLS_BY_KEY["esd"].precaution


def test_kits_follow_the_inventory_and_every_tool_is_used():
    used = {k for i in INTERVENTIONS for k in i.tools}
    assert used == {t.key for t in TOOLS}
    ram = next(i for i in INTERVENTIONS if i.key == "ram")
    assert [t.key for t in kit(ram)] == ["tournevis", "esd"]
    prise = next(i for i in INTERVENTIONS if i.key == "prise")
    assert [t.key for t in kit(prise)] == ["sertisseuse-rj45", "denudeur", "insertion", "wiremap"]
    for intervention in INTERVENTIONS:
        assert set(intervention.risks) <= {r.key for r in RISKS}, intervention.key


def test_risks_cover_ticket_and_safety_rules():
    keys = [r.key for r in RISKS]
    assert keys == ["esd", "elec", "psu", "batt", "vent", "meca", "laser", "poste"]
    by_key = {r.key: r for r in RISKS}
    assert "jamais un bloc" in by_key["psu"].prevention
    assert "ne pas la charger" in by_key["batt"].prevention and "112" in by_key["batt"].reaction
    assert "infrarouge" in by_key["laser"].danger and "ne jamais regarder" in by_key["laser"].prevention
    assert "couper le courant avant de toucher" in by_key["elec"].reaction


def test_disconnection_order():
    labels = [label for label, _d in DISCONNECT_STEPS]
    assert labels == ["Prévenir", "Arrêter le système", "Couper le bloc", "Débrancher", "Vider les charges",
                      "Se protéger de l'ESD"]


def test_power_supply_tolerances_reused_from_pr02():
    assert [r.name for r in RAILS if not within_tolerance(r, E06_MEASURED[r.name])] == ["+12 V"]
    assert [r.name for r in RAILS if not within_tolerance(r, X02_MEASURED[r.name])] == ["+5 V"]
    # recontrôle indépendant : 11,31 < 12 × 0,95 = 11,4 ; 4,71 < 5 × 0,95 = 4,75
    assert E06_MEASURED["+12 V"] < 11.4 and X02_MEASURED["+5 V"] < 4.75


def test_rule_321():
    pc, ext, nas = Copy("a", SUP_INTERNAL, False), Copy("b", SUP_EXTERNAL, False), Copy("c", SUP_NAS, False)
    cloud, key = Copy("d", SUP_CLOUD, True), Copy("e", SUP_USB_KEY, True)
    assert check_321((pc, ext, cloud)) == ()
    assert check_321((pc, cloud)) == (MISS_3,)
    assert check_321((pc, ext, nas)) == (MISS_2, MISS_1)  # trois disques sur place
    assert check_321((pc, nas, key)) == ()
    assert check_321((pc,)) == (MISS_3, MISS_2, MISS_1)
    assert check_321(X05_COPIES) == (MISS_2, MISS_1)
    assert [len(check_321(c)) for _t, c in E11_PLANS] == [0, 1, 1, 1, 1, 0]


def test_fingerprints_and_copy_integrity():
    assert fingerprint("abc") == hashlib.sha256(b"abc").hexdigest()[:16] == "ba7816bf8f01cfea"
    src = (("a", 1, "x"), ("b", 2, "y"), ("c", 3, "z"))
    assert compare_copy(src, (("a", 1, "x"), ("c", 3, "w"))) == (("b",), ("c",))
    assert compare_copy(src, src) == ((), ())
    missing, different = compare_copy(E12_SOURCE, E12_COPY)
    assert missing == ("Tarifs.xlsx",) and different == ("Radios-octobre.zip",)
    # même taille, contenu différent : seule l'empreinte le révèle
    size = {n: s for n, s, _f in E12_COPY}
    assert size["Radios-octobre.zip"] == {n: s for n, s, _f in E12_SOURCE}["Radios-octobre.zip"]


def test_prerequisites_before_erasing():
    full = required_prerequisites(OP_REINSTALL, keep_data=True, encrypted=True)
    assert full == (PRE_BACKUP, PRE_CONSENT, PRE_AUTHORIZED, PRE_KEY, PRE_LICENSES)
    assert required_prerequisites(OP_ERASE, keep_data=False, encrypted=True) == (PRE_CONSENT, PRE_AUTHORIZED)
    assert PRE_KEY not in required_prerequisites(OP_REINSTALL, keep_data=True, encrypted=False)
    assert missing_prerequisites(OP_REINSTALL, frozenset(full), keep_data=True, encrypted=True) == ()
    with pytest.raises(ValueError):
        required_prerequisites("Défragmentation", keep_data=True, encrypted=False)


def test_waste_routes():
    assert waste_route(W_EEE) == ROUTE_EEE and "Recupel" in ROUTE_EEE
    assert waste_route(W_BATTERY) == ROUTE_BATTERY and "Bebat" in ROUTE_BATTERY and "isolés" in ROUTE_BATTERY
    assert waste_route(W_DATA) == ROUTE_DATA and "Effacement certifié ou destruction" in ROUTE_DATA


def test_incident_tree_puts_people_first():
    questions = [q for q, _n in INCIDENT_TREE.questions]
    assert "zone" in questions[0] and "indemne" in questions[1]
    assert "données" in questions[2] and "matériel" in questions[3]
    assert walk(INCIDENT_TREE, (False,))[0] == 1 and "112" in walk(INCIDENT_TREE, (False,))[1]
    assert walk(INCIDENT_TREE, (True, True, True, True))[0] is None


# =============================================================================================
# 2. Cinq interventions résolues
# =============================================================================================


def test_five_cases_cover_ticket_themes_with_computed_values():
    assert len(CASES) == 5
    assert [c.theme for c in CASES] == ["outillage et sécurité du poste", "batterie endommagée", "données du client",
                                       "outillage réseau et fibre", "fin de vie et DEEE"]
    assert C3_321_BEFORE == (MISS_3, MISS_2, MISS_1) and C3_321_AFTER == ()
    assert C3_INTEGRITY == (("Contrats.docx",), ("Factures-sept.zip",))
    assert C3_MISSING == (PRE_BACKUP, PRE_KEY, PRE_LICENSES)
    assert C5_HDD_OK is True and C5_SSD_FORMAT_OK is False
    assert {route for _i, route in C5_ROUTES} == {ROUTE_EEE, ROUTE_DATA, ROUTE_BATTERY, waste_route("cartouche d'encre ou toner")}
    c3 = next(c for c in CASES if c.key == "C3")
    assert "Contrats.docx" in " ".join(c3.before) and "clé de récupération" in " ".join(c3.before)
    c4 = next(c for c in CASES if c.key == "C4")
    assert {"wiremap", "fibre-nettoyage", "vfl", "insertion"} <= {t.key for t in c4.tools}
    for case in CASES:
        assert case.before and case.during and case.after and len(case.context) >= 150, case.key


# =============================================================================================
# 3. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    figures = list(PR28_FIGURES) + [f for f, _p in STATIC_FIGURES]
    assert len({f.key for f in figures}) == len(figures)
    for figure in figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "non officiel" in html


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR28_FIGURES}
    assert by_key["pr28-outils-pc"].svg.count('data-tool="') == sum(t.family.startswith("Poste") for t in TOOLS)
    assert by_key["pr28-outils-reseau"].svg.count('data-tool="') == sum(t.family.startswith("Réseau") for t in TOOLS)
    for i, (label, _d) in enumerate(DISCONNECT_STEPS, start=1):
        assert f"{i}. {escape(label)}" in by_key["pr28-procedure-debranchement"].svg
    esd = by_key["pr28-poste-esd"]
    assert esd.svg.count('data-badge="') == len(ESD_PARTS)
    for n, label in ESD_PARTS:
        assert f"{n}. {escape(label)}" in esd.svg
    rule = by_key["pr28-regle-321"]
    assert rule.svg.count('data-copy="') == 3 and rule.svg.count("✓") == 3 and "✗" not in rule.svg
    assert by_key["pr28-filieres-deee"].svg.count('data-waste="') == 4
    assert by_key["pr28-arbre-incident"].svg.count('data-step="') == len(INCIDENT_TREE.questions)
    assert by_key["pr28-liste-controle"].svg.count("☐") == 10


def test_schemas_to_complete_hide_their_answers():
    esd, _p = STATIC_FIGURES[0]
    for _n, label in ESD_PARTS:
        first_words = " ".join(label.split()[:2])
        assert escape(first_words) not in esd.svg and first_words not in esd.alt, label
    assert "sachet" not in esd.svg and "point de masse" not in esd.svg
    tree, _p = STATIC_FIGURES[1]
    assert set(INCIDENT_BLANK_ANSWERS) == {"①", "②", "③", "④"}
    for answer in INCIDENT_BLANK_ANSWERS.values():
        first_words = " ".join(answer.split()[:3])
        assert escape(first_words) not in tree.svg and first_words not in tree.alt


def test_static_figure_files_are_the_generated_svg():
    for figure, path in STATIC_FIGURES:
        assert (STATIC_DIR / path).read_text(encoding="utf-8") == static_svg(figure), path


# =============================================================================================
# 4. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 18 and len(EXAM_ITEMS) == 10  # ticket : ≥ 18 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_SCHEMA) == 2 and kinds.count(KIND_ORDER) >= 4 and kinds.count(KIND_TREE) >= 1
    assert kinds.count(KIND_TOOL) >= 4 and kinds.count(KIND_DATA) >= 5 and kinds.count(KIND_WRITE) >= 2
    assert {d.image for i in PRACTICE_ITEMS for d in i.documents if d.image} == {p for _f, p in STATIC_FIGURES}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        assert REQ & set(item.requirement_ids), item.key


def test_auto_corrected_answers():
    e01 = _item("E01").classification
    for element, category in zip(e01.elements, e01.correct, strict=True):
        assert e01.categories[category] == TOOLS_BY_KEY[dict(TASKS)[element]].name
    e03 = _item("E03").ordering
    assert [e03.steps[i].split(" — ")[0] for i in e03.correct] == [label for label, _d in DISCONNECT_STEPS]
    e04 = _item("E04").ordering
    assert [e04.steps[i].split(" — ")[0] for i in e04.correct][:3] == ["Ne plus charger", "Ne pas déformer", "Isoler"]
    e09 = _item("E09").ordering
    assert [e09.steps[i] for i in e09.correct][-1].startswith("Tester")
    assert [e09.steps[i] for i in e09.correct][1].startswith("Retirer la gaine")
    e08 = _item("E08").classification
    for element, category in zip(e08.elements, e08.correct, strict=True):
        bad = re.search(r"aspirateur|librement|sous tension|capot du bloc|déborde", element)
        assert (category == 1) == bool(bad), element
    e11 = _item("E11").classification
    assert e11.categories[e11.correct[0]] == "Conforme à la règle 3-2-1"
    e15 = _item("E15").classification
    for element, category in zip(e15.elements, e15.correct, strict=True):
        if "atterie" in element or "piles" in element.lower():
            assert e15.categories[category] == ROUTE_BATTERY, element


def test_values_in_corrections_match_calculations():
    assert "+12 V" in _item("E06").criteria[0].expected and "11,40 V à 12,60 V" in _item("E06").criteria[0].expected
    assert "+5 V" in _item("X02").criteria[0].expected and "4,75 V à 5,25 V" in _item("X02").criteria[0].expected
    assert "Tarifs.xlsx" in _item("E12").criteria[0].expected and "Radios-octobre.zip" in _item("E12").criteria[0].expected
    assert "Photos-chantier.zip" in _item("X06").criteria[0].expected and "Métrés.xlsx" in _item("X06").criteria[0].expected
    assert PRE_CONSENT in _item("E14").criteria[0].expected and PRE_AUTHORIZED in _item("E14").criteria[0].expected
    assert PRE_KEY in _item("X07").criteria[0].expected and PRE_BACKUP not in _item("X07").criteria[0].expected
    assert MISS_2 in _item("X05").criteria[0].expected and MISS_1 in _item("X05").criteria[0].expected
    assert "Question 4" in _item("E22").criteria[0].expected and "Question 1" in _item("X10").criteria[0].expected
    assert _item("X04").criteria[0].label == "Étape 3" and _item("X04").criteria[1].label == "Étape 5"
    assert "Bebat" in _item("X09").criteria[0].expected and "Recupel" in _item("X09").criteria[0].expected
    for t in kit(next(i for i in INTERVENTIONS if i.key == "cmos")):
        assert t.name in _item("E05").criteria[0].expected


def test_schema_documents_point_to_static_files():
    layout = _document_layout(_item("E16").documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr28-poste-esd-a-completer.svg"
    assert "non officiel" in layout["notice"]
    layout = _document_layout(_item("E17").documents[0])
    assert layout["src"] == "/static/img/ampcr-pratique/pr28-arbre-incident-a-completer.svg" and "①" in layout["alt"]


def test_no_bad_practice_presented_as_right():
    text = (_course_text() + " " + _all_items_text().lower()).replace("’", "'")
    for wrong in ("ouvrir le bloc pour le nettoyer est", "on peut regarder la fibre", "recharger la batterie gonflée pour",
                  "un formatage rapide suffit", "l'accord oral suffit", "jeter la batterie à la poubelle",
                  "mesurer le 230 v avec le multimètre est"):
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
# 5. Cours
# =============================================================================================


def test_five_cases_procedures_and_exam_not_in_course():
    raw = _course_raw()
    text = _text(raw)
    assert text.count("Conclusion rédigée.") == 5
    for i in (1, 2, 3, 4, 5):
        assert f"Procédure {i} —" in text and f"Intervention {i} —" in text, i
    for item in EXAM_ITEMS:
        assert item.context not in raw and escape(item.context) not in raw, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in raw, item.key
    for figure in list(PR28_FIGURES) + [f for f, _p in STATIC_FIGURES]:
        assert f'id="fig-{figure.key}"' in raw, figure.key
    assert escape("Fiche sécurité (modèle du cours, exemple rempli)") in raw
    assert escape("Choisir le kit selon l'intervention (inventaire du cours)") in raw


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr28_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        "tournevis", "pinces", "bracelet", "tapis", "selon la procédure", "testeur d'alimentation", "autorisé",
        "multimètre", "pâte thermique", "nettoyage", "sertisseuse 8p8c", "dénudeur", "outil d'insertion",
        "wiremap", "bnc", "fibre", "sécurité laser", "esd", "électricité", "jamais un bloc", "batterie",
        "ventilation", "risques mécaniques", "poste de travail", "débrancher", "3-2-1", "complément", "intégrité",
        "confidentialité", "chiffrement", "droits", "données du client", "autorisation", "effacement",
        "réinstallation", "deee", "fiche sécurité", "choisir l'outil", "incident", "liste de contrôle",
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    assert "AP-C02" in text and "AP-C03" in text and "AP-14" in text and "AP-20" in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "font foi" in text
    for link in ("/uaa/ampcr-mc05", "/uaa/ampcr-mc06", "/uaa/ampcr-mc32", "/uaa/ampcr-pratique-pr02",
                 "/uaa/ampcr-pratique-pr03", "/uaa/ampcr-pratique-pr04", "/uaa/ampcr-pratique-pr05",
                 "/uaa/ampcr-pratique-pr12", "/uaa/ampcr-pratique-pr15", "/uaa/ampcr-pratique-pr16",
                 "/uaa/ampcr-pratique-pr17", "/uaa/ampcr-pratique-pr18", "/uaa/ampcr-pratique-pr22",
                 "/uaa/ampcr-pratique-pr23", "/uaa/ampcr-pratique-pr26", "/uaa/ampcr-pratique-pr27",
                 f"/uaa/{PR28_SLUG}/practice", f"/uaa/{PR28_SLUG}/exam"):
        assert link in raw, link
    for unpublished in ("/uaa/ampcr-pratique-pr29", "/uaa/ampcr-pratique-pr30"):
        assert unpublished not in raw
    anchors = set(re.findall(r'id="(pr28-e\d\d)"', raw))
    assert anchors == {f"pr28-{i.key.lower()}" for i in PRACTICE_ITEMS}


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr28_course_sections()]
    assert kinds[:9] == ["theory"] * 9
    assert kinds[9:] == ["example", "warning", "exercise", "exam", "summary", "info"]


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR28"]
    assert slot.ticket == 227 and slot.title == PR28_TITLE == PRACTICAL_COURSES_BY_CODE["PR28"].title
    assert slot.requirement_ids == ("AP-C02", "AP-C03")


# =============================================================================================
# 6. Seed, banque, correction
# =============================================================================================


def test_seed_publishes_pr28_in_practical_module_idempotently(db_session):
    module, uaa = _pr28(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR28_TITLE and uaa.position == 28
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR28").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr28_course_sections())
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR27") + 1 == ordered.index("PR28")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr28(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr28_specific():
    context = _pedagogical_context_for("PR28")
    assert context is get_practical_context("PR28")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("selon la procédure de l'atelier", "jamais le 230 V", "±5 %", "bloc jamais ouvert",
                   "ne jamais regarder une fibre", "3 copies original compris", "SHA-256", "clé de récupération",
                   "personne habilitée", "Recupel", "Bebat", "72 h"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "ouvrir un bloc" in context.constraints


# =============================================================================================
# 7. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr28(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR28_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200
    for linked in ("ampcr-mc05", "ampcr-mc06", "ampcr-mc32", "ampcr-pratique-pr02", "ampcr-pratique-pr04",
                   "ampcr-pratique-pr12", "ampcr-pratique-pr17", "ampcr-pratique-pr27"):
        assert client.get(f"/uaa/{linked}").status_code == 200, linked


def test_practical_home_and_matrix_show_pr28(client, db_session):
    _pr28(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr28(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR28"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr28(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR28", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr28(db_session)
    for _ in range(3):  # 22 exercices : trois sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

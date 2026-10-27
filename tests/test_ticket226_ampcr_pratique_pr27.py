"""Ticket #226 — AMPCR pratique écrite, PR27 « Construire et justifier une procédure de diagnostic ».

Couvre : règles du cours **recontrôlées ici** indépendamment (cycle, échelle d'invasivité et
précautions, tri des tests, test croisé, faux positifs / négatifs, contrôle de configuration,
facteur commun, hypothèses restantes, quatre arbres) ; six dossiers résolus (tests discriminants
et ordonnés, cause unique, chemin dans l'arbre cohérent avec la conclusion) ; schémas SVG
(validité, accessibilité, données dessinées, schémas à compléter sans leurs réponses, fichiers
statiques) ; exercices et mini-examen (format du socle, auto-correction, valeurs des corrigés) ;
cours (matière du ticket, procédures, liens, supports fictifs, cartes) ; banque, seed, pages et
sessions. Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr27_bank import (
    E04_CASES,
    E07_DIFF,
    E09_FACTORS,
    E12_RESTARTS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_ORDER,
    KIND_SCHEMA,
    KIND_TEST,
    KIND_TREE,
    KIND_WRITE,
    PRACTICE_ITEMS,
    REQ,
    X05_DIFF,
    X07_FACTORS,
    validate_items,
)
from app.v1.ampcr_pratique_pr27_course import PR27_SLUG, PR27_TITLE, pr27_course_sections
from app.v1.ampcr_pratique_pr27_figures import (
    BOOT_BLANK_ANSWERS,
    CASES,
    CROSS_BOTH,
    CROSS_HOST,
    CROSS_NONE,
    CROSS_PART,
    D6_FACTORS,
    FALSE_NEGATIVE,
    FALSE_POSITIVE,
    FALSE_RESULTS,
    LEVELS,
    METHOD_STEPS,
    NET_BLANK_ANSWERS,
    NET_LAYERS,
    P_BACKUP,
    P_POWER,
    P_STATE,
    PR27_FIGURES,
    STATIC_FIGURES,
    TREE_BOOT,
    TREE_NETWORK,
    TREES,
    Probe,
    common_factors,
    config_diff,
    cross_test,
    is_discriminant,
    order_probes,
    precautions,
    remaining,
    static_svg,
    walk,
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

SLUG = "ampcr-pratique-pr27"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr27_course_sections())


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


def _pr27(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR27")
    return module, uaa


# =============================================================================================
# 1. Règles du cours, recontrôlées indépendamment
# =============================================================================================


def test_cycle_matches_ticket_order():
    assert [label for label, _d in METHOD_STEPS] == [
        "Hypothèse", "Test discriminant", "Résultat attendu", "Interprétation", "Action", "Validation"]
    assert "AVANT" in METHOD_STEPS[2][1]


def test_invasiveness_scale_and_precautions():
    assert [lv.number for lv in LEVELS] == [0, 1, 2, 3, 4, 5]
    assert precautions(0) == precautions(1) == ()
    assert P_STATE in precautions(3) and P_STATE not in precautions(2)
    assert P_POWER in precautions(4) and P_POWER not in precautions(5)  # une réinstallation ne s'ouvre pas
    assert P_BACKUP in precautions(5) and P_BACKUP not in precautions(4)
    for level in range(2, 6):
        assert set(precautions(2)) <= set(precautions(level)), level
    with pytest.raises(ValueError):
        precautions(6)
    probes = (Probe("c", 2, 10), Probe("a", 0, 30), Probe("d", 2, 5), Probe("b", 1, 1))
    assert [p.label for p in order_probes(probes)] == ["a", "b", "d", "c"]


def test_cross_test_truth_table():
    assert cross_test(False, True) == CROSS_PART  # la panne suit l'élément
    assert cross_test(True, False) == CROSS_HOST  # la panne reste sur le poste
    assert cross_test(False, False) == CROSS_BOTH
    assert cross_test(True, True) == CROSS_NONE
    assert [cross_test(a, b) for _t, a, b in E04_CASES] == [
        CROSS_PART, CROSS_HOST, CROSS_NONE, CROSS_BOTH, CROSS_PART, CROSS_HOST]


def test_false_results_are_unambiguous():
    for text, kind, _why in FALSE_RESULTS:
        # faux positif : une panne « signalée » ; faux négatif : un test qui « réussit » à tort
        signals = bool(re.search(r"échoue|coupure|aucun signal|semble morte", text, re.IGNORECASE))
        assert signals == (kind == FALSE_POSITIVE), text
    assert sum(k == FALSE_NEGATIVE for _t, k, _w in FALSE_RESULTS) == 4


def test_config_diff_and_common_factors():
    assert config_diff({"a": "1", "b": "2", "c": "3"}, {"a": "1", "b": "9", "c": " 3 "}) == ("b",)
    assert config_diff({"a": "1"}, {}) == ("a",)
    assert E07_DIFF == ("Masque", "Passerelle") and X05_DIFF == ("Passerelle",)
    header = ("x", "y", "panne")
    rows = (("1", "u", "oui"), ("1", "v", "oui"), ("2", "u", "non"))
    assert common_factors(header, rows, outcome="panne", failure="oui") == (("x", "1"),)
    # une valeur commune aux pannes mais vue aussi sans panne n'est pas un facteur
    rows2 = (("1", "u", "oui"), ("1", "u", "oui"), ("1", "v", "non"))
    assert common_factors(header, rows2, outcome="panne", failure="oui") == (("y", "u"),)
    assert D6_FACTORS == (("Activité de la réceptionniste", "recule sa chaise vers l'imprimante"),)
    assert E09_FACTORS == (("Imprimante inactive depuis plus d'une heure", "oui"),)
    assert X07_FACTORS == (("Station d'accueil branchée", "oui"),)


def test_remaining_and_discriminant():
    expected = ("a", "b", "b")
    assert remaining(expected, "b", (0, 1, 2)) == (1, 2)
    assert remaining(expected, "a", (1, 2)) == ()
    assert is_discriminant(expected, (0, 1, 2)) and not is_discriminant(expected, (1, 2))


def test_four_trees_and_walk():
    assert {t.key for t in TREES} == {"materiel", "demarrage", "systeme", "reseau"}
    for tree in TREES:
        assert len(tree.questions) >= 5, tree.key
        assert walk(tree, (True,) * len(tree.questions)) == (None, tree.final)
        for n in range(1, len(tree.questions) + 1):
            assert walk(tree, (True,) * (n - 1) + (False,)) == (n, tree.questions[n - 1][1])
    with pytest.raises(ValueError):
        walk(TREE_NETWORK, (False, True))
    with pytest.raises(ValueError):
        walk(TREE_NETWORK, (True, True))
    net = [q for q, _n in TREE_NETWORK.questions]
    assert "169.254" in net[1] and "passerelle" in net[2] and "nslookup" in net[4]
    boot = [q for q, _n in TREE_BOOT.questions]
    assert "signe de vie" in boot[0] and "ordre de démarrage" in boot[3]


# =============================================================================================
# 2. Six dossiers résolus
# =============================================================================================


def test_cases_cover_ticket_themes():
    assert [c.theme for c in CASES] == [
        "démarrage", "périphérique", "DHCP", "DNS", "partage", "panne intermittente"]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.key)
def test_case_tests_are_ordered_discriminant_and_lead_to_one_cause(case):
    levels = [(t.level, t.minutes) for t in case.tests]
    assert levels == sorted(levels), case.key
    for i, test in enumerate(case.tests):
        alive = case.alive_before(i)
        assert len(test.expected) == len(case.hypotheses), case.key
        assert is_discriminant(test.expected, alive), (case.key, i)
        assert test.observed in {test.expected[h] for h in alive}, (case.key, i)
    assert case.cause is not None, case.key
    assert len(case.validation) >= 2


def test_case_causes_and_tree_paths():
    by_key = {c.key: c for c in CASES}
    assert {k: c.cause for k, c in by_key.items()} == {"D1": 0, "D2": 2, "D3": 2, "D4": 2, "D5": 1, "D6": 0}
    assert {k: c.tree_result[0] for k, c in by_key.items()} == {
        "D1": 4, "D2": 3, "D3": 2, "D4": 5, "D5": None, "D6": 1}
    assert "Ordre de démarrage" in by_key["D1"].tree_result[1]
    assert "DHCP" in by_key["D3"].tree_result[1] and "DNS" in by_key["D4"].tree_result[1]
    assert "partage" in by_key["D5"].tree_result[1]
    # escalade quand l'action sort des droits du technicien
    assert by_key["D3"].escalation.startswith("Oui") and by_key["D5"].escalation.startswith("Oui")
    assert "semaine" in " ".join(by_key["D6"].validation)  # panne intermittente : validation sur une durée


# =============================================================================================
# 3. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    figures = list(PR27_FIGURES) + [f for f, _p in STATIC_FIGURES]
    assert len({f.key for f in figures}) == len(figures)
    for figure in figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "non officiel" in html


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR27_FIGURES}
    flow = by_key["pr27-cycle-diagnostic"]
    for i, (label, _d) in enumerate(METHOD_STEPS, start=1):
        assert f"{i}. {escape(label)}" in flow.svg
    ladder = by_key["pr27-echelle-invasivite"]
    assert ladder.svg.count('data-level="') == 6
    layers = by_key["pr27-couches-reseau"]
    assert layers.svg.count('data-layer="') == len(NET_LAYERS)
    cross = by_key["pr27-test-croise"]
    assert cross.svg.count('data-cross="') == 4 and "panne non reproduite" in cross.alt.lower()
    for tree in TREES:
        figure = by_key[f"pr27-arbre-{tree.key}"]
        assert figure.svg.count('data-step="') == len(tree.questions), tree.key


def test_schemas_to_complete_hide_their_answers():
    for (figure, _p), answers in zip(STATIC_FIGURES, (NET_BLANK_ANSWERS, BOOT_BLANK_ANSWERS), strict=True):
        assert set(answers) == {"①", "②", "③", "④"}
        for answer in answers.values():
            first_words = " ".join(answer.split()[:3])
            assert escape(first_words) not in figure.svg and first_words not in figure.alt, figure.key


def test_static_figure_files_are_the_generated_svg():
    for figure, path in STATIC_FIGURES:
        assert (STATIC_DIR / path).read_text(encoding="utf-8") == static_svg(figure), path


# =============================================================================================
# 4. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 20 and len(EXAM_ITEMS) == 10
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_ORDER) >= 8  # ticket : ≥ 8 procédures à ordonner / justifier
    assert kinds.count(KIND_SCHEMA) == 2 and kinds.count(KIND_TREE) >= 2
    assert kinds.count(KIND_TEST) >= 5 and kinds.count(KIND_WRITE) >= 3
    assert {d.image for i in PRACTICE_ITEMS for d in i.documents if d.image} == {p for _f, p in STATIC_FIGURES}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        assert REQ & set(item.requirement_ids), item.key


def test_auto_corrected_answers():
    e01 = _item("E01").ordering
    assert [e01.steps[i].split(" — ")[0] for i in e01.correct] == [label for label, _d in METHOD_STEPS]
    e02 = _item("E02").ordering
    assert [e02.steps[i] for i in e02.correct] == [
        "Demander à l'utilisateur depuis quand et pendant quelle tâche",
        "Lire le Gestionnaire des tâches et l'Observateur d'événements",
        "Redémarrer le poste après lui avoir fait enregistrer son travail",
        "Démarrage minimal : désactiver les programmes tiers lancés au démarrage",
        "Ouvrir le boîtier pour dépoussiérer le ventilateur du processeur",
        "Réinstaller Windows après sauvegarde et accord écrit",
    ]
    e23 = _item("E23").ordering
    assert [e23.steps[i].split(" — ")[0] for i in e23.correct] == [
        "Physique", "Liaison", "Réseau (IP)", "Transport", "Application"]
    e03 = _item("E03").classification
    assert [e03.correct[i] for i in range(len(e03.elements))] == [0, 1, 1, 2, 2, 3, 3, 4, 5, 5]
    e05 = _item("E05").classification
    assert [e05.categories[c].split()[1] for c in e05.correct] == ["positif"] * 4 + ["négatif"] * 4


def test_values_in_corrections_match_calculations():
    assert "T4" in _item("E06").criteria[0].expected and "H2 et H3" in _item("E06").criteria[1].expected
    assert "H2 câble vidéo défectueux" in _item("E06").criteria[2].expected
    assert "Masque et Passerelle" in _item("E07").criteria[0].expected
    assert E12_RESTARTS == 3 and "3 : 8 → 4 → 2 → 1" in _item("E12").criteria[1].expected
    assert "Question 3" in _item("E12").criteria[0].expected and "Question 4" in _item("E13").criteria[0].expected
    assert "c → d → a → b" in _item("E22").criteria[0].expected
    assert "c → d → b → a" in _item("X02").criteria[0].expected
    assert CROSS_HOST in _item("X03").criteria[0].expected
    assert "Question 3" in _item("X09").criteria[0].expected
    assert "b → e → d → a → f → c" in " ".join(_item("E16").correction)


def test_schema_documents_point_to_static_files():
    layout = _document_layout(_item("E10").documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr27-arbre-reseau-a-completer.svg"
    assert "①" in layout["alt"] and "non officiel" in layout["notice"]


def test_no_bad_practice_presented_as_right():
    text = (_course_text() + " " + _all_items_text().lower()).replace("’", "'")
    for wrong in ("réinstaller d'abord", "commencer par réinstaller", "changer plusieurs éléments à la fois pour gagner",
                  "l'événement 41 est la cause", "un seul essai réussi suffit", "nettoyer soi-même le poste compromis est"):
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


def test_six_cases_four_trees_procedures_and_exam_not_in_course():
    raw = _course_raw()
    text = _text(raw)
    examples = dict(pr27_course_sections())["PR27 — Exemples : six dossiers de diagnostic entièrement résolus"]
    assert text.count("Conclusion rédigée.") == 6 and examples.count("tests du moins au plus invasif") == 6
    for i in (1, 2, 3, 4):
        assert f"Procédure {i} —" in text and f"Arbre {i} —" in text, i
    for item in EXAM_ITEMS:
        assert item.context not in raw and escape(item.context) not in raw, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in raw, item.key
    for figure in list(PR27_FIGURES) + [f for f, _p in STATIC_FIGURES]:
        assert f'id="fig-{figure.key}"' in raw, figure.key
    assert escape("Plan de retour arrière (modèle du cours)") in raw
    assert escape("Procédure de diagnostic écrite (modèle du cours)") in raw


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr27_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        "hypothèse", "test discriminant", "résultat attendu", "interprétation", "action", "validation",
        "moins invasif", "plus invasif", "approche par couches", "isolation de variables", "test croisé",
        "contrôle de configuration", "journaux", "logs", "conditions de reproduction", "arbres décisionnels",
        "matériel", "démarrage", "système", "réseau", "test négatif", "faux positif", "alternatives", "escalade",
        "conservation de preuves", "plan de retour arrière", "mesure d'impact", "sécurité",
        "démarrage", "périphérique", "dhcp", "dns", "partage", "panne intermittente",
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    assert "AP-15" in text and "Dépannage sur les dysfonctionnements courants" in text and "AP-C01" in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "convention" in text.lower() and "l'entreprise fait foi" in _course_text()
    for link in ("/uaa/ampcr-mc29", "/uaa/ampcr-mc30", "/uaa/ampcr-pratique-pr26", "/uaa/ampcr-pratique-pr06",
                 "/uaa/ampcr-pratique-pr12", "/uaa/ampcr-pratique-pr20", "/uaa/ampcr-pratique-pr23",
                 "/uaa/ampcr-pratique-pr24", f"/uaa/{PR27_SLUG}/practice", f"/uaa/{PR27_SLUG}/exam"):
        assert link in raw, link
    for unpublished in ("/uaa/ampcr-pratique-pr28", "/uaa/ampcr-pratique-pr29", "/uaa/ampcr-pratique-pr30"):
        assert unpublished not in raw
    anchors = set(re.findall(r'id="(pr27-e\d\d)"', raw))
    assert anchors == {f"pr27-{i.key.lower()}" for i in PRACTICE_ITEMS}


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr27_course_sections()]
    assert kinds[:9] == ["theory"] * 9
    assert kinds[9:] == ["example", "warning", "exercise", "exam", "summary", "info"]


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR27"]
    assert slot.ticket == 226 and slot.title == PR27_TITLE == PRACTICAL_COURSES_BY_CODE["PR27"].title
    assert slot.requirement_ids == ("AP-15", "AP-C01")


# =============================================================================================
# 6. Seed, banque, correction
# =============================================================================================


def test_seed_publishes_pr27_in_practical_module_idempotently(db_session):
    module, uaa = _pr27(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR27_TITLE and uaa.position == 27
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR27").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr27_course_sections())
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR26") + 1 == ordered.index("PR27")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr27(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr27_specific():
    context = _pedagogical_context_for("PR27")
    assert context is get_practical_context("PR27")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("test discriminant", "écrit AVANT", "à niveau égal le plus rapide", "test croisé",
                   "faux positif", "41 et EventLog 6008", "facteur présent à chaque panne", "Restaurer le pilote"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "sans sauvegarde" in context.constraints


# =============================================================================================
# 7. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr27(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR27_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200
    for linked in ("ampcr-mc29", "ampcr-mc30", "ampcr-pratique-pr26", "ampcr-pratique-pr06", "ampcr-pratique-pr12",
                   "ampcr-pratique-pr20", "ampcr-pratique-pr23", "ampcr-pratique-pr24"):
        assert client.get(f"/uaa/{linked}").status_code == 200, linked


def test_practical_home_and_matrix_show_pr27(client, db_session):
    _pr27(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr27(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR27"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr27(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR27", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr27(db_session)
    for _ in range(3):  # 23 exercices : trois sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

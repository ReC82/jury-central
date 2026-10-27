"""Ticket #228 — AMPCR pratique écrite, PR29 « Contrôles finaux et rapport professionnel
d'intervention ».

Couvre : règles du cours **recontrôlées ici** indépendamment (familles de contrôles et contrôles
exigés, critères avant / après, verdict, décision, arbre de clôture, journal, test reproductible,
rubriques du rapport, données sensibles, grille sur 20) ; cinq rapports modèles (valeurs
calculées, rubriques complètes, aucune donnée sensible) ; schémas SVG et formulaires
imprimables (validité, accessibilité, données dessinées, schémas à compléter sans leurs réponses,
fichiers statiques) ; exercices et mini-examen (format du socle, auto-correction, valeurs des
corrigés) ; cours (matière du ticket, liens, supports fictifs, cartes) ; banque, seed, pages et
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
from app.v1.ampcr_pratique_pr27_figures import walk
from app.v1.ampcr_pratique_pr29_bank import (
    E03_MEASURES,
    E06_JOURNAL,
    E19_MARKS,
    E19_SCORE,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_COMM,
    KIND_FIX,
    KIND_ORDER,
    KIND_SCHEMA,
    KIND_TREE,
    KIND_WRITE,
    PRACTICE_ITEMS,
    REQ,
    X04_LINES,
    validate_items,
)
from app.v1.ampcr_pratique_pr29_course import PR29_SLUG, PR29_TITLE, pr29_course_sections
from app.v1.ampcr_pratique_pr29_figures import (
    C_BOOT,
    C_FILES,
    C_SPEED,
    CHECK_FAMILIES,
    CRITERIA_STATEMENTS,
    D_ESCALATE,
    D_FOLLOWUP,
    D_ROLLBACK,
    D_SIGN,
    DECISION_TREE,
    DOC_ITEMS,
    DOC_TARGETS,
    FINAL_STEPS,
    GRID_TOTAL,
    INCONCLUSIVE,
    INTERVENTION_KINDS,
    K_HW,
    K_OS,
    K_SHARE,
    MEASURABLE,
    MESSAGES,
    MET,
    MSG_TECH,
    MSG_WRONG,
    NOT_MET,
    NOT_TO_WRITE,
    PR29_FIGURES,
    PRINTABLE_FORMS,
    PRINTABLE_PATHS,
    REPORT_BLANK_ANSWERS,
    REPORT_FIELDS,
    REPORT_GRID,
    REPORT_MENTIONS,
    REPORTS,
    REPORTS_BY_KEY,
    REPRO_FIELDS,
    ROLLBACK_STEPS,
    STATIC_FIGURES,
    TREE_BLANK_ANSWERS,
    V_REJECT,
    V_RESERVE,
    V_VALID,
    Criterion,
    JournalEntry,
    assess,
    decision,
    fmt,
    journal_issues,
    missing_checks,
    missing_report_fields,
    printable_form_html,
    report_score,
    repro_missing,
    required_checks,
    sensitive_lines,
    static_svg,
    verdict,
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

SLUG = "ampcr-pratique-pr29"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr29_course_sections())


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


def _pr29(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR29")
    return module, uaa


# =============================================================================================
# 1. Règles du cours, recontrôlées indépendamment
# =============================================================================================


def test_six_check_families_of_the_ticket():
    assert [f.name for f in CHECK_FAMILIES] == ["Test fonctionnel", "Stabilité", "Performance",
                                                "Réseau local et Internet", "Sécurité", "Pilote et périphérique"]
    assert all(f.tests and f.question and f.evidence for f in CHECK_FAMILIES)


def test_required_checks_always_include_functional_and_security():
    for kind in INTERVENTION_KINDS:
        keys = [f.key for f in required_checks(kind)]
        assert "fonctionnel" in keys and "securite" in keys, kind
    assert [f.key for f in required_checks(K_HW)] == ["fonctionnel", "stabilite", "performance", "securite"]
    assert {"reseau", "pilote"} <= {f.key for f in required_checks(K_OS)}
    assert [f.key for f in missing_checks(K_SHARE, frozenset({"fonctionnel"}))] == ["reseau", "securite"]
    with pytest.raises(ValueError):
        required_checks("Défragmentation")


def test_assess_and_verdict():
    assert assess(C_BOOT, 42) == MET and assess(C_BOOT, 60) == MET and assess(C_BOOT, 75) == NOT_MET
    assert assess(C_SPEED, 1000) == MET and assess(C_SPEED, 100) == NOT_MET
    assert assess(C_FILES, "oui") == MET and assess(C_FILES, "non") == NOT_MET
    assert assess(C_BOOT, None) == INCONCLUSIVE
    with pytest.raises(TypeError):
        assess(C_BOOT, "rapide")
    assert verdict((MET, MET)) == V_VALID
    assert verdict((MET, INCONCLUSIVE)) == V_RESERVE
    assert verdict((INCONCLUSIVE, NOT_MET)) == V_REJECT  # un non atteint l'emporte
    with pytest.raises(ValueError):
        verdict(())
    # « mieux qu'avant » n'est pas « atteint » : 150 s → 75 s pour une cible de 60 s
    boot = next(m for m in E03_MEASURES if m.criterion is C_BOOT)
    assert boot.after < boot.before and boot.result == NOT_MET


def test_decision_rules():
    assert decision(V_VALID, rollback_ready=False) == D_SIGN
    assert decision(V_RESERVE, rollback_ready=True) == D_FOLLOWUP
    assert decision(V_REJECT, rollback_ready=True) == D_ROLLBACK
    assert decision(V_REJECT, rollback_ready=False) == D_ESCALATE
    with pytest.raises(ValueError):
        decision("Réparé", rollback_ready=True)


def test_closing_tree_order_and_walk():
    questions = [q for q, _n in DECISION_TREE.questions]
    assert "contrôles exigés" in questions[0] and "critères" in questions[1]
    assert "concluants" in questions[2] and "client" in questions[3]
    assert walk(DECISION_TREE, (True, False))[0] == 2 and "Retour arrière" in walk(DECISION_TREE, (True, False))[1]
    assert "réserve" in walk(DECISION_TREE, (True, True, False))[1]
    assert walk(DECISION_TREE, (True, True, True, True))[0] is None


def test_journal_issues_and_reproducible_tests():
    ok = (JournalEntry("09:00", "a", "valeur 1"), JournalEntry("09:05", "b", "valeur 2"))
    assert journal_issues(ok) == ()
    bad = (JournalEntry("09:10", "a", "OK"), JournalEntry("09:00", "b", ""))
    assert journal_issues(bad) == ("Ligne 1 : résultat vague (« OK »), non vérifiable",
                                   "Ligne 2 : heure antérieure à la ligne précédente (ordre chronologique)",
                                   "Ligne 2 : résultat absent")
    assert len(journal_issues(E06_JOURNAL)) == 3
    with pytest.raises(ValueError):
        journal_issues((JournalEntry("9h", "a", "b"),))
    assert len(REPRO_FIELDS) == 6
    full = {k: "x" for k, _l in REPRO_FIELDS}
    assert repro_missing(full) == () and len(repro_missing({})) == 6


def test_report_fields_follow_ticket_and_sensitive_detection():
    labels = " ".join(f.label.lower() for f in REPORT_FIELDS)
    for rubric in ("équipement (identité non sensible)", "demande", "symptômes", "hypothèses", "relevés", "tests",
                   "résultats", "action", "pièces", "validation", "risques résiduels", "recommandation",
                   "signature et accord"):
        assert rubric in labels, rubric
    assert len(REPORT_FIELDS) == 14 and len({f.key for f in REPORT_FIELDS}) == 14
    assert missing_report_fields({}) == tuple(f.label for f in REPORT_FIELDS)
    assert sensitive_lines(("mot de passe : abc", "Équipement INV-0412", "clé de récupération : 123456-654321",
                            "Carte 4111 1111 1111 1111 visible", "J'ai consulté les photos du dossier Images")) == (
        (1, "mot de passe"), (3, "clé de récupération"), (4, "numéro de carte bancaire"),
        (5, "contenu des fichiers personnels"))
    assert [n for n, _k in sensitive_lines(X04_LINES)] == [3, 5]
    assert {k for _t, k in REPORT_MENTIONS} == {"À écrire dans le rapport", NOT_TO_WRITE}


def test_report_grid_on_20():
    assert GRID_TOTAL == sum(p for _k, _l, p, _d in REPORT_GRID) == 20
    assert report_score({k: 1 for k, *_r in REPORT_GRID}) == 20
    assert report_score({}) == 0
    assert E19_SCORE == report_score(E19_MARKS) == 4.5  # 3 × 0,5 + 2 × 1 + 2 × 0,5
    with pytest.raises(ValueError):
        report_score({"structure": 0.7})


def test_fmt_french_numbers():
    assert fmt(11.31) == "11,31" and fmt(2.5) == "2,5" and fmt(1000) == "1000" and fmt(None) == "non mesuré"
    assert Criterion("Démarrage", "<=", 60, "s").text() == "Démarrage ≤ 60 s"


# =============================================================================================
# 2. Cinq rapports modèles
# =============================================================================================


def test_five_model_reports_cover_ticket_themes_with_computed_values():
    assert [r.theme for r in REPORTS] == ["PC (matériel)", "système d'exploitation", "câblage RJ45", "réseau",
                                         "partage de dossiers"]
    for report in REPORTS:
        assert missing_report_fields(report.filled()) == (), report.key
        assert report.missing_checks == (), report.key
        assert sensitive_lines(tuple(report.filled().values())) == (), report.key
        assert journal_issues(report.journal) == (), report.key
        assert len(report.context) >= 150 and report.client_message, report.key
        # l'avant ne satisfait pas au moins un critère : le rapport prouve un changement
        assert any(assess(m.criterion, m.before) != MET for m in report.measures), report.key
    assert [r.verdict for r in REPORTS] == [V_VALID, V_VALID, V_VALID, V_RESERVE, V_VALID]
    assert REPORTS_BY_KEY["R4"].decision == D_FOLLOWUP and REPORTS_BY_KEY["R1"].decision == D_SIGN
    assert "Retour arrière" in " ".join(e.action for e in REPORTS_BY_KEY["R2"].journal)
    assert "réserve" in REPORTS_BY_KEY["R4"].fields["signature"].lower()


# =============================================================================================
# 3. Schémas et formulaires
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    figures = list(PR29_FIGURES) + [f for f, _p in STATIC_FIGURES]
    assert len({f.key for f in figures}) == len(figures)
    for figure in figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "non officiel" in html


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR29_FIGURES}
    assert by_key["pr29-familles-controles"].svg.count('data-family="') == len(CHECK_FAMILIES)
    structure = by_key["pr29-structure-rapport"].svg
    assert structure.count('data-section="') == 6
    for field in REPORT_FIELDS:
        assert escape(field.label) in structure, field.label
    r3 = by_key["pr29-avant-apres"].svg
    assert r3.count('data-measure="atteint"') == 3 and "✗" not in r3
    r4 = by_key["pr29-avant-apres-reserve"].svg
    assert r4.count('data-measure="non concluant"') == 1 and "?" in r4
    assert by_key["pr29-arbre-cloture"].svg.count('data-step="') == len(DECISION_TREE.questions)
    for i, (label, _d) in enumerate(FINAL_STEPS, start=1):
        assert f"{i}. {escape(label)}" in by_key["pr29-procedure-controles"].svg
    assert by_key["pr29-liste-cloture"].svg.count("☐") == 9


def test_schemas_to_complete_hide_their_answers():
    report, _p = STATIC_FIGURES[0]
    assert set(REPORT_BLANK_ANSWERS) == {"①", "②", "③", "④"}
    for label in REPORT_BLANK_ANSWERS.values():
        assert escape(label) not in report.svg and label not in report.alt, label
    tree, _p = STATIC_FIGURES[1]
    assert set(TREE_BLANK_ANSWERS) == {"①", "②", "③", "④"}
    for answer in TREE_BLANK_ANSWERS.values():
        first_words = " ".join(answer.split()[:3])
        assert escape(first_words) not in tree.svg and first_words not in tree.alt


def test_static_files_are_the_generated_content():
    for figure, path in STATIC_FIGURES:
        assert (STATIC_DIR / path).read_text(encoding="utf-8") == static_svg(figure), path
    for form in PRINTABLE_FORMS:
        assert (STATIC_DIR / PRINTABLE_PATHS[form.key]).read_text(encoding="utf-8") == printable_form_html(form)


def test_printable_forms_are_a4_self_contained_and_complete():
    assert len(PRINTABLE_FORMS) == 3
    for form in PRINTABLE_FORMS:
        html = printable_form_html(form)
        assert "@page{size:A4" in html and "<script" not in html.lower() and "http" not in html
        assert 'lang="fr"' in html and "non officiel" in html
    report = printable_form_html(next(f for f in PRINTABLE_FORMS if f.key == "pr29-formulaire-rapport"))
    for field in REPORT_FIELDS:
        assert escape(field.label) in report, field.label
    checks = printable_form_html(next(f for f in PRINTABLE_FORMS if f.key == "pr29-formulaire-controles"))
    for family in CHECK_FAMILIES:
        assert escape(family.name) in checks
    assert checks.index("Critères d&#x27;acceptation") < checks.index("Verdict et décision")


# =============================================================================================
# 4. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 18 and len(EXAM_ITEMS) == 10  # ticket : ≥ 18 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_SCHEMA) == 2 and kinds.count(KIND_ORDER) >= 2 and kinds.count(KIND_TREE) >= 1
    # ticket : exercices de correction de rapports et de rédaction
    assert kinds.count(KIND_FIX) >= 4 and kinds.count(KIND_WRITE) >= 2 and kinds.count(KIND_COMM) >= 2
    assert {d.image for i in PRACTICE_ITEMS for d in i.documents if d.image} == {p for _f, p in STATIC_FIGURES}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        assert REQ & set(item.requirement_ids), item.key


def test_auto_corrected_answers():
    e01 = _item("E01").classification
    assert len(set(e01.correct)) == 6
    by_text = {"Chronométrer le démarrage jusqu'au bureau": "Performance",
               "Supprimer le compte technique créé pour l'intervention": "Sécurité",
               "Imprimer une page de test et essayer la webcam": "Pilote et périphérique"}
    for element, category in zip(e01.elements, e01.correct, strict=True):
        if element in by_text:
            assert e01.categories[category] == by_text[element], element
    e04 = _item("E04").classification
    for element, category in zip(e04.elements, e04.correct, strict=True):
        assert (e04.categories[category] == MEASURABLE) == bool(re.search(r"\d|ouvre et enregistre", element)), element
    e05 = _item("E05").ordering
    assert [e05.steps[i].split(" — ")[0] for i in e05.correct] == [label for label, _d in FINAL_STEPS]
    e13 = _item("E13").ordering
    assert [e13.steps[i].split(" — ")[0] for i in e13.correct] == [label for label, _d in ROLLBACK_STEPS]
    e08 = _item("E08").classification
    for element, category in zip(e08.elements, e08.correct, strict=True):
        secret = re.search(r"mot de passe|clé de récupération|carte bancaire|photos|avis personnel", element.lower())
        assert (e08.categories[category] == NOT_TO_WRITE) == bool(secret), element
    e11 = _item("E11").classification
    for element, category in zip(e11.elements, e11.correct, strict=True):
        if re.search(r"SMART|paire 3-6|DHCP", element):
            assert e11.categories[category] == MSG_TECH, element
        if re.search(r"jamais\.|comme neuf|votre faute|sûrement cassé", element):
            assert e11.categories[category] == MSG_WRONG, element
    e21 = _item("E21").classification
    assert e21.categories == DOC_TARGETS
    assert [e21.categories[c] for c in e21.correct] == [t for _i, t in DOC_ITEMS]


def test_values_in_corrections_match_calculations():
    assert "Réseau local et Internet" in _item("E02").criteria[1].expected and "Pilote" in _item("E02").criteria[1].expected
    assert "75 → non atteint" in _item("E03").criteria[0].expected and "Non validé" in _item("E03").criteria[1].expected
    e06 = _item("E06").criteria[0].expected
    assert "Ligne 3" in e06 and "Ligne 4" in e06 and "Ligne 5" in e06
    assert "Relevés" in _item("E09").criteria[0].expected and "Recommandation" in _item("E09").criteria[0].expected
    assert "réserve" in _item("E10").criteria[1].expected
    assert D_ROLLBACK in _item("E14").criteria[1].expected and D_ESCALATE.lower() in _item("E14").criteria[1].expected
    assert "Question 3" in _item("E17").criteria[0].expected and "Question 2" in _item("X08").criteria[0].expected
    assert "Note 4" in _item("E18").criteria[3].expected
    assert "4,5/20" in _item("E19").criteria[0].expected
    assert "Stabilité" in _item("X01").criteria[0].expected and "Sécurité" in _item("X01").criteria[0].expected
    assert "2 → non atteint" in _item("X02").criteria[0].expected
    assert "ligne 3" in _item("X04").criteria[0].expected and "ligne 5" in _item("X04").criteria[0].expected
    assert D_ESCALATE.lower() in _item("X07").criteria[0].expected
    assert "non concluant" in _item("X09").criteria[0].expected


def test_schema_documents_point_to_static_files():
    layout = _document_layout(_item("E15").documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr29-arbre-cloture-a-completer.svg"
    assert "non officiel" in layout["notice"]
    layout = _document_layout(_item("E16").documents[0])
    assert layout["src"] == "/static/img/ampcr-pratique/pr29-structure-rapport-a-completer.svg" and "①" in layout["alt"]


def test_no_bad_practice_presented_as_right():
    text = (_course_text() + " " + _all_items_text().lower()).replace("’", "'")
    for wrong in ("c'est mieux, donc c'est validé", "ok suffit comme résultat", "on peut noter le mot de passe",
                  "un résultat non concluant est validé", "on peut promettre"):
        assert wrong not in text, wrong
    # les phrases trompeuses n'apparaissent que comme contre-exemples classés
    for statement, kind in MESSAGES:
        if kind == MSG_WRONG:
            assert statement in [e for e in _item("E11").classification.elements]
    assert [k for _t, k in CRITERIA_STATEMENTS].count(MEASURABLE) == 5


def test_no_acronym_question_and_full_context():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.title, item.context, *item.instructions))
        assert not re.search(r"que signifie|que veut dire|développe[rz]? l'acronyme", text, re.IGNORECASE), item.key
        assert len(item.context) >= 150, item.key
        assert "officiel" not in item.title.lower(), item.key


def test_document_references_match_document_count():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.context, *item.instructions))
        for n in re.findall(r"document (\d)", text):
            assert int(n) <= len(item.documents), (item.key, n)


def test_items_content_matches_existing_question_types():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        content = item_content(item, list(range(1, len(item.documents) + 1)))
        validate_content(item.question_type, 1, content)


# =============================================================================================
# 5. Cours
# =============================================================================================


def test_five_reports_procedures_and_exam_not_in_course():
    raw = _course_raw()
    text = _text(raw)
    assert text.count("Message au client (non technique).") == 5
    for i in (1, 2, 3, 4):
        assert f"Procédure {i} —" in text, i
    for i in (1, 2, 3, 4, 5):
        assert f"Rapport {i} —" in text, i
    for item in EXAM_ITEMS:
        assert item.context not in raw and escape(item.context) not in raw, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in raw, item.key
    for figure in list(PR29_FIGURES) + [f for f, _p in STATIC_FIGURES]:
        assert f'id="fig-{figure.key}"' in raw, figure.key
    for form in PRINTABLE_FORMS:
        assert f"/static/{PRINTABLE_PATHS[form.key]}" in raw, form.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr29_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        "critères d'acceptation", "avant / après", "test fonctionnel", "stabilité", "performance",
        "réseau local et internet", "sécurité", "pilote et périphérique", "journal des opérations",
        "reproductible", "restauration", "retour arrière", "non concluant", "limites", "identité",
        "n° d'inventaire", "demande", "symptômes", "hypothèses", "relevés", "tests", "résultats", "action",
        "pièces", "validation", "risques résiduels", "recommandation", "signature", "accord",
        "non technique", "escalade", "documenter", "base de connaissances", "formulaires imprimables",
        "vocabulaire technique", "confidentialité", "régression", "réserve",
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    assert "AP-16" in text and "AP-C01" in text and "AP-15" in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "font foi" in text or "fait foi" in text
    for link in ("/uaa/ampcr-mc29", "/uaa/ampcr-mc30", "/uaa/ampcr-mc36", "/uaa/ampcr-pratique-pr02",
                 "/uaa/ampcr-pratique-pr08", "/uaa/ampcr-pratique-pr12", "/uaa/ampcr-pratique-pr15",
                 "/uaa/ampcr-pratique-pr23", "/uaa/ampcr-pratique-pr24", "/uaa/ampcr-pratique-pr26",
                 "/uaa/ampcr-pratique-pr27", "/uaa/ampcr-pratique-pr28",
                 f"/uaa/{PR29_SLUG}/practice", f"/uaa/{PR29_SLUG}/exam"):
        assert link in raw, link
    assert "/uaa/ampcr-pratique-pr30" not in raw
    anchors = set(re.findall(r'id="(pr29-e\d\d)"', raw))
    assert anchors == {f"pr29-{i.key.lower()}" for i in PRACTICE_ITEMS}


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr29_course_sections()]
    assert kinds[:9] == ["theory"] * 9
    assert kinds[9:] == ["example", "warning", "exercise", "exam", "summary", "info"]


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR29"]
    assert slot.ticket == 228 and slot.title == PR29_TITLE == PRACTICAL_COURSES_BY_CODE["PR29"].title
    assert slot.requirement_ids == ("AP-16", "AP-C01")


# =============================================================================================
# 6. Seed, banque, correction
# =============================================================================================


def test_seed_publishes_pr29_in_practical_module_idempotently(db_session):
    module, uaa = _pr29(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR29_TITLE and uaa.position == 29
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR29").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr29_course_sections())
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR28") + 1 == ordered.index("PR29")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr29(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr29_specific():
    context = _pedagogical_context_for("PR29")
    assert context is get_practical_context("PR29")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("même si mieux qu'avant", "non concluant", "fonctionnel et sécurité toujours exigés",
                   "« OK »", "retour arrière puis vérification", "14 rubriques", "mot de passe", "sur 20",
                   "base de connaissances"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "régression cachée" in context.constraints


# =============================================================================================
# 7. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_exercises_and_forms(client, db_session):
    _pr29(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR29_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200
    for form in PRINTABLE_FORMS:
        page = client.get(f"/static/{PRINTABLE_PATHS[form.key]}")
        assert page.status_code == 200 and "text/html" in page.headers["content-type"]
    for linked in ("ampcr-mc29", "ampcr-mc36", "ampcr-pratique-pr26", "ampcr-pratique-pr27", "ampcr-pratique-pr28"):
        assert client.get(f"/uaa/{linked}").status_code == 200, linked


def test_practical_home_and_matrix_show_pr29(client, db_session):
    _pr29(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr29(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR29"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr29(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR29", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr29(db_session)
    for _ in range(3):  # 22 exercices : trois sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

"""Ticket #225 — AMPCR pratique écrite, PR26 « Analyser une demande d'intervention technique ».

Couvre : règles du cours **recontrôlées ici** indépendamment (matrice impact × urgence, délais,
ordre des contrôles d'escalade, rubriques obligatoires de la fiche, estimation + 25 % au quart
d'heure, grille sur 20) ; cinq dossiers corrigés (priorité, estimation et escalade calculées,
cohérentes avec la fiche affichée) ; schémas SVG (validité, accessibilité, données dessinées,
schémas à compléter sans leurs réponses, fichiers statiques) ; exercices et mini-examen (format
du socle, auto-correction, valeurs des corrigés) ; cours (matière du ticket, procédures,
formulaires, grille, liens, supports fictifs, cartes) ; banque, seed, pages et sessions. Aucun
appel IA réel : `FakeAIProvider` partout."""

import re
from html import escape
from pathlib import Path

import pytest

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_audit import proven_requirement_ids as audit_proven_ids
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    _document_layout,
    get_practical_context,
    import_practical_bank,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_pr26_bank import (
    E04_CASES,
    E06_CASES,
    E09_FICHE,
    E14_ESTIMATE,
    E19_MARKS,
    E19_SCORE,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_ORDER,
    KIND_QUALIF,
    KIND_SCHEMA,
    KIND_TICKET,
    KIND_WRITE,
    PRACTICE_ITEMS,
    REQ,
    X08_ESTIMATE,
    validate_items,
)
from app.v1.ampcr_pratique_pr26_course import PR26_SLUG, PR26_TITLE, pr26_course_sections
from app.v1.ampcr_pratique_pr26_figures import (
    ANALYSIS_STEPS,
    DOSSIERS,
    ESCALATION_CHECKS,
    ESCALATION_KEYS,
    EVAL_GRID,
    EVAL_TOTAL,
    HIGH,
    INCIDENT_FIELDS,
    LOW,
    MATRIX_BLANK_ANSWERS,
    MEDIUM,
    OCCURRENCES,
    PR26_FIGURES,
    PRIORITY_LABELS,
    PRIORITY_MATRIX,
    REQUIRED_KEYS,
    STATEMENTS,
    STATIC_FIGURES,
    TREE_BLANK_ANSWERS,
    Situation,
    escalation,
    estimate,
    grid_score,
    missing_fields,
    priority,
    static_svg,
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

SLUG = "ampcr-pratique-pr26"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr26_course_sections())


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


def _pr26(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR26")
    return module, uaa


# =============================================================================================
# 1. Règles du cours, recontrôlées indépendamment
# =============================================================================================


def test_priority_matrix_recomputed_by_hand():
    expected = {
        (1, 1): "P1", (1, 2): "P2", (2, 1): "P2", (1, 3): "P3", (2, 2): "P3", (3, 1): "P3",
        (2, 3): "P4", (3, 2): "P4", (3, 3): "P4",
    }
    for (impact, urgency), p in expected.items():
        assert priority(impact, urgency) == p, (impact, urgency)
    assert PRIORITY_MATRIX == (("P1", "P2", "P3"), ("P2", "P3", "P4"), ("P3", "P4", "P4"))
    with pytest.raises(ValueError):
        priority(0, 2)


def test_escalation_order_and_first_failure():
    assert ESCALATION_KEYS == ("securite", "autorisation", "donnees", "competence", "budget")
    assert escalation(Situation()) is None
    for key in ESCALATION_KEYS:
        assert escalation(Situation(**{key: False})) == key
    # la sécurité passe avant les données, les droits avant le budget
    assert escalation(Situation(securite=False, donnees=False)) == "securite"
    assert escalation(Situation(autorisation=False, budget=False)) == "autorisation"
    assert "isoler" in ESCALATION_CHECKS[0][2].lower() and "ne rien effacer" in ESCALATION_CHECKS[0][2].lower()


def test_incident_form_and_missing_fields():
    sections = [f.section for f in INCIDENT_FIELDS]
    assert len(dict.fromkeys(sections)) == 6
    assert {"symptomes", "changements", "utilisateurs", "impact", "urgence", "priorite", "sauvegarde",
            "confidentialite", "autorisation", "reformulation", "criteres", "plan", "escalade",
            "inventaire"} <= set(REQUIRED_KEYS)
    assert missing_fields({k: "x" for k in REQUIRED_KEYS}) == ()
    assert missing_fields({}) == REQUIRED_KEYS
    assert missing_fields(E09_FICHE) == ("inventaire", "apparition", "changements", "sauvegarde", "autorisation",
                                         "reformulation")


def test_estimate_and_grid():
    assert estimate((30, 25, 60, 30, 20)) == 210 == E14_ESTIMATE  # 165 × 1,25 = 206,25 → 210
    assert estimate((10, 50, 30)) == 120 == X08_ESTIMATE  # 90 × 1,25 = 112,5 → 120
    assert estimate((12,)) == 15 and estimate((24,)) == 30  # 15 tout juste, puis quart supérieur
    assert EVAL_TOTAL == 20 == sum(p for _k, _l, p, _d in EVAL_GRID)
    assert grid_score({k: 1 for k, *_r in EVAL_GRID}) == 20
    assert E19_SCORE == 2 + 1.5 + 2 + 0 + 1.5 + 0 + 1 + 2 + 1 == 11 == grid_score(E19_MARKS)
    with pytest.raises(ValueError):
        grid_score({"symptomes": 0.3})


def test_statements_and_occurrences_are_unambiguous():
    for text, kind in STATEMENTS:
        is_hyp = kind.startswith("Hypothèse")
        assert is_hyp == bool(re.search(r"sûrement|en panne|a dû|trop faible|incompatible", text)), text
    for text, kind in OCCURRENCES:
        repro = kind == "Panne reproductible"
        assert repro == bool(re.search(r"chaque|toujours", text)), text


def test_dossiers_cover_ticket_and_are_consistent():
    titles = " ".join(d.title.lower() for d in DOSSIERS)
    for subject in ("pc inerte", "impression", "lenteur", "partagé", "wi-fi"):
        assert subject in titles, subject
    for d in DOSSIERS:
        assert d.field("priorite") == PRIORITY_LABELS[d.priority], d.key
        assert not missing_fields(dict(d.fiche)), d.key
        assert ("Oui" in d.field("escalade")) == (d.escalation is not None), d.key
        assert d.priority in d.conclusion, d.key
    by_key = {d.key: d for d in DOSSIERS}
    assert by_key["D4"].priority == "P1" and by_key["D4"].escalation == "autorisation"
    assert by_key["D5"].occurrence == "Panne intermittente"
    assert [d.estimate_minutes for d in DOSSIERS] == [60, 60, 105, 60, 105]


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    figures = list(PR26_FIGURES) + [f for f, _p in STATIC_FIGURES]
    assert len({f.key for f in figures}) == len(figures)
    for figure in figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "non officiel" in html


def test_figures_drawn_from_data():
    matrix = next(f for f in PR26_FIGURES if f.key == "pr26-matrice-priorite")
    for impact in (HIGH, MEDIUM, LOW):
        for urgency in (HIGH, MEDIUM, LOW):
            assert f'data-cell="{impact}-{urgency}"' in matrix.svg
    assert matrix.svg.count(">critique<") == 1 and matrix.svg.count(">basse<") == 3
    flow = next(f for f in PR26_FIGURES if f.key == "pr26-procedure-analyse")
    for i, (label, _d) in enumerate(ANALYSIS_STEPS, start=1):
        assert f"{i}. {escape(label)}" in flow.svg
    tree = next(f for f in PR26_FIGURES if f.key == "pr26-arbre-escalade")
    assert tree.svg.count('data-step="') == len(ESCALATION_CHECKS)
    form = next(f for f in PR26_FIGURES if f.key == "pr26-fiche-incident")
    for field in INCIDENT_FIELDS:
        assert escape(field.label) in form.svg, field.key


def test_schemas_to_complete_hide_their_answers():
    matrix, _p = STATIC_FIGURES[0]
    assert MATRIX_BLANK_ANSWERS == {"①": "P2 haute", "②": "P3 normale", "③": "P3 normale", "④": "P4 basse"}
    assert matrix.svg.count(">critique<") == 1 and ">haute<" in matrix.svg  # case (2,1) visible
    assert matrix.svg.count('fill="#ffffff"') >= 4
    tree, _p = STATIC_FIGURES[1]
    for answer in TREE_BLANK_ANSWERS.values():
        first_words = " ".join(answer.split()[:3])
        assert escape(first_words) not in tree.svg and first_words not in tree.alt


def test_static_figure_files_are_the_generated_svg():
    for figure, path in STATIC_FIGURES:
        assert (STATIC_DIR / path).read_text(encoding="utf-8") == static_svg(figure), path


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 18 and len(EXAM_ITEMS) == 10
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_SCHEMA) == 2 and kinds.count(KIND_ORDER) == 1
    assert kinds.count(KIND_WRITE) >= 5 and kinds.count(KIND_TICKET) >= 5 and kinds.count(KIND_QUALIF) >= 5
    assert {d.image for i in PRACTICE_ITEMS for d in i.documents if d.image} == {p for _f, p in STATIC_FIGURES}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        assert REQ & set(item.requirement_ids), item.key


def test_auto_corrected_answers():
    e04 = _item("E04").classification
    assert [e04.categories[c] for c in e04.correct] == [
        "P1 critique", "P2 haute", "P4 basse", "P4 basse", "P3 normale", "P3 normale", "P1 critique"]
    assert [priority(i, u) for _t, i, u in E04_CASES] == [c.split()[0] for c in (e04.categories[x] for x in e04.correct)]
    e06 = _item("E06").classification
    assert [e06.categories[c] for c in e06.correct] == [
        "Traiter directement", "Arrêter et escalader", "Arrêter et escalader", "Arrêter et escalader",
        "Traiter directement", "Arrêter et escalader", "Arrêter et escalader"]
    assert [escalation(s) for _t, s in E06_CASES][2] == "securite"
    e02 = _item("E02").classification
    assert [e02.categories[c].split()[0] for c in e02.correct] == ["Observation", "Hypothèse"] * 4
    e05 = _item("E05").classification
    assert [e05.categories[c] for c in e05.correct].count("Question à éviter") == 3
    ordering = _item("E01").ordering
    assert [ordering.steps[i].split(" — ")[0] for i in ordering.correct] == [label for label, _d in ANALYSIS_STEPS]


def test_values_in_corrections_match_calculations():
    assert "3 h 30" in _item("E14").criteria[1].expected and "206,25" in _item("E14").criteria[1].expected
    assert "2 h" in _item("X08").criteria[0].expected and "112,5" in _item("X08").criteria[0].expected
    assert "11 / 20" in _item("E19").criteria[0].expected
    assert "P2 haute" in _item("E12").criteria[2].expected and "P2 haute" in _item("X03").criteria[1].expected
    assert "P3 normale" in _item("E11").criteria[2].expected
    e09 = _item("E09").criteria[0].expected
    for label in ("N° d'inventaire", "Changements récents", "Données et sauvegarde", "Reformulation"):
        assert label in e09, label
    x04 = _item("X04").criteria[0].expected
    assert "Changements récents" in x04 and "Critères de réussite" in x04 and "Utilisateurs touchés" in x04


def test_schema_documents_point_to_static_files():
    layout = _document_layout(_item("E07").documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr26-matrice-a-completer.svg"
    assert "①" in layout["alt"] and "non officiel" in layout["notice"]


def test_no_bad_practice_presented_as_right():
    text = (_course_text() + " " + _all_items_text().lower()).replace("’", "'")
    for right in ("observation", "hypothèse", "reproductible", "intermittente", "impact", "urgence", "priorité",
                  "sauvegarde", "confidentialité", "consentement", "autorisation", "reformulation",
                  "critère de réussite", "plan d'action", "estimation", "escalade", "fiche d'incident",
                  "inventaire", "changements récents", "utilisateurs touchés"):
        assert right in text, right
    for wrong in ("réinstaller sans sauvegarde est", "donner le mot de passe de son collègue est",
                  "élargir les droits pour tester est conseillé", "la priorité choisie par l'utilisateur fait foi",
                  "un seul essai réussi suffit"):
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


def test_five_dossiers_procedures_forms_and_exam_not_in_course():
    raw = _course_raw()
    text = _text(raw)
    examples = dict(pr26_course_sections())["PR26 — Exemples : cinq dossiers entièrement corrigés"]
    assert text.count("Conclusion rédigée.") == 5 and examples.count("<caption>Fiche INT-2610-") == 5
    for i in (1, 2, 3):
        assert f"Procédure {i} —" in text, i
    for item in EXAM_ITEMS:
        assert item.context not in raw and escape(item.context) not in raw, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in raw, item.key
    for figure in list(PR26_FIGURES) + [f for f, _p in STATIC_FIGURES]:
        assert f'id="fig-{figure.key}"' in raw, figure.key
    assert escape("Bon d'accord avant une opération risquée") in raw
    assert escape("Grille d'évaluation d'une fiche d'incident") in raw


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr26_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        "demande", "symptômes", "interprétation", "contexte matériel, logiciel et réseau", "utilisateurs touchés",
        "date", "changements récents", "impact", "urgence", "priorisation", "inventaire", "références",
        "consentement", "confidentialité", "sauvegarde", "risques", "autorisation", "reformulation",
        "questions utiles", "fiche d'incident", "critères de réussite", "plan d'action", "estimation", "escalade",
        "reproductible", "intermittente", "observation", "hypothèse", "formulaire professionnel",
        "grille d'évaluation", "vocabulaire technique",
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    assert "AP-16" in text and "Vocabulaire technique." in text and "AP-C01" in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "convention" in text.lower() and "l'entreprise fait foi" in _course_text()
    for link in ("/uaa/ampcr-mc36", "/uaa/ampcr-pratique-pr06", "/uaa/ampcr-pratique-pr12",
                 "/uaa/ampcr-pratique-pr23", "/uaa/ampcr-pratique-pr24", "/uaa/ampcr-pratique-pr25",
                 f"/uaa/{PR26_SLUG}/practice", f"/uaa/{PR26_SLUG}/exam"):
        assert link in raw, link
    for unpublished in ("/uaa/ampcr-pratique-pr27", "/uaa/ampcr-pratique-pr28", "/uaa/ampcr-pratique-pr29"):
        assert unpublished not in raw
    anchors = set(re.findall(r'id="(pr26-e\d\d)"', raw))
    assert anchors == {f"pr26-{i.key.lower()}" for i in PRACTICE_ITEMS}


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr26_course_sections()]
    assert kinds[:10] == ["theory"] * 10
    assert kinds[10:] == ["example", "warning", "exercise", "exam", "summary", "info"]


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR26"]
    assert slot.ticket == 225 and slot.title == PR26_TITLE == PRACTICAL_COURSES_BY_CODE["PR26"].title
    assert slot.requirement_ids == ("AP-16", "AP-C01")


# =============================================================================================
# 5. Seed, banque, correction
# =============================================================================================


def test_seed_publishes_pr26_in_practical_module_idempotently(db_session):
    module, uaa = _pr26(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR26_TITLE and uaa.position == 26
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR26").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr26_course_sections())
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR25") < ordered.index("EX04") < ordered.index("PR26")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr26(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr26_specific():
    context = _pedagogical_context_for("PR26")
    assert context is get_practical_context("PR26")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("1+1 → P1", "+ 25 %", "quart d'heure", "sécurité (isoler", "observation = fait",
                   "panne intermittente", "grille sur 20", "« si je résume bien… »"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "sans sauvegarde" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_forms_and_exercises(client, db_session):
    _pr26(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR26_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200
    for linked in ("ampcr-mc36", "ampcr-pratique-pr06", "ampcr-pratique-pr12", "ampcr-pratique-pr23",
                   "ampcr-pratique-pr24", "ampcr-pratique-pr25"):
        assert client.get(f"/uaa/{linked}").status_code == 200, linked


def test_practical_home_and_matrix_show_pr26(client, db_session):
    _pr26(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR27 (#226) publié ensuite
    assert plan.VALIDATED_REQUIREMENT_IDS == audit_proven_ids()  # « validé » : preuves de l'audit #235
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr26(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR26"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr26(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR26", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr26(db_session)
    for _ in range(2):  # 20 exercices : deux sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

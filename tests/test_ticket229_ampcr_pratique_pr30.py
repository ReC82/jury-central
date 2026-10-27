"""Ticket #229 — AMPCR pratique écrite, PR30 « Grand laboratoire écrit — installation et
dépannage d'un réseau complet ».

Couvre : dossier de la PME **recontrôlé ici** indépendamment (longueurs, dimensionnement,
budget sans prix, T568B, plan IPv4 sans erreur, brouillon fautif, modèle de comptes, matrice
des droits conforme aux besoins, compatibilité Windows 11, Wi-Fi, couverture, recette, verdict
et rapport) ; huit études de cas graduées reliées aux exigences officielles ; schémas SVG
(validité, accessibilité, données dessinées, schémas à compléter sans leurs réponses, fichiers
statiques) ; exercices et mini-examen (format du socle, auto-correction, valeurs des
corrigés) ; cours (matière du ticket, liens, supports fictifs, cartes) ; banque, seed, pages et
sessions. Aucun appel IA réel : `FakeAIProvider` partout."""

import ipaddress
import math
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
from app.v1.ampcr_pratique_pr29_figures import D_FOLLOWUP, INCONCLUSIVE, REPORT_FIELDS, V_RESERVE
from app.v1.ampcr_pratique_pr30_bank import (
    E05_CORRECT,
    E05_TESTS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_ORDER,
    KIND_SCHEMA,
    KIND_TREE,
    KIND_WRITE,
    PRACTICE_ITEMS,
    REQ,
    X01_BOXES,
    X01_LENGTHS,
    X01_SWITCH,
    validate_items,
)
from app.v1.ampcr_pratique_pr30_course import PR30_SLUG, PR30_TITLE, pr30_course_sections
from app.v1.ampcr_pratique_pr30_figures import (
    AP_AUDIT,
    BOM,
    CABLE_BOXES,
    CASES,
    CHANNEL_24,
    COST_GROUPS,
    DRAFT_ERRORS,
    FAILED_LINKS,
    FINAL_REPORT,
    FOLDERS,
    HOSTS,
    LINK_RESULTS,
    LINKS,
    MATRIX,
    MODEL,
    MODEL_LATER,
    NEIGHBORS,
    NOT_COVERED_OFFICIAL,
    OS_PLAN,
    PANELS,
    PASSPHRASE_PRO,
    PINS,
    PLAN,
    PLAN_ERRORS,
    POE_RESULT,
    POOL,
    PORTS_LATER,
    PORTS_NOW,
    PR30_FIGURES,
    RACK_BLANK_ANSWERS,
    RACK_U,
    RACK_USED_U,
    RECETTE_DIAG,
    RECETTE_TREE,
    REQ_TASKS,
    RUNS,
    SECURITY_ITEMS,
    STATIC_FIGURES,
    STORED_ACCESS,
    SURVEY_ROWS,
    SWITCH_PORTS,
    TOTAL_CABLE_M,
    TREE_BLANK_ANSWERS,
    WORST_5,
    access,
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

SLUG = "ampcr-pratique-pr30"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr30_course_sections())


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


def _pr30(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR30")
    return module, uaa


# =============================================================================================
# 1. Dossier de la PME, recontrôlé indépendamment
# =============================================================================================


def test_dossier_has_the_ticket_scope():
    # ticket : plan de 2 salles, 6 postes Windows/Linux, switch, routeur/AP, imprimante, partage et serveur
    salles = [r for r in PLAN.rooms if r.name.startswith("Salle")]
    assert len(salles) == 2
    assert len(OS_PLAN) == 6 and set(OS_PLAN.values()) == {"Windows 11 Pro", "Ubuntu 24.04 LTS (bureau)"}
    names = {h.name for h in HOSTS}
    assert {"BOX", "SW-01", "AP-01", "SRV-01", "IMP-01"} <= names
    assert len(FOLDERS) == 4


def test_lengths_and_dimensioning_recomputed():
    rack = PLAN.rack
    for (key, horizontal, length), outlet in zip(RUNS, PLAN.outlets, strict=True):
        assert key == outlet.key
        assert horizontal == abs(rack.x - outlet.x) + abs(rack.y - outlet.y)
        assert length == math.ceil(horizontal + 3 + 2)
        assert length <= 90
    assert TOTAL_CABLE_M == sum(r[2] for r in RUNS) and CABLE_BOXES == math.ceil(TOTAL_CABLE_M / 305)
    assert LINKS == 10
    assert PORTS_NOW == math.ceil(10 * 1.2) + 2 == 14
    assert PORTS_LATER == math.ceil(14 * 1.2) + 2 == 19
    assert SWITCH_PORTS == 24 and PANELS == 1
    assert RACK_USED_U == 12 and RACK_U == 15 and RACK_U >= RACK_USED_U * 1.25
    assert POE_RESULT == "Budget suffisant"


def test_budget_has_no_invented_price():
    assert {b.group for b in BOM} == set(COST_GROUPS)
    text = " ".join(f"{b.item} {b.quantity} {b.why}" for b in BOM)
    assert "€" not in text and not re.search(r"\beuros?\b|\bprix\b", text, re.IGNORECASE)


def test_t568b_and_link_tests():
    assert [c for _p, c in PINS] == ["blanc-orange", "orange", "blanc-vert", "bleu", "blanc-bleu", "vert",
                                     "blanc-marron", "marron"]
    assert FAILED_LINKS == ("P08",)
    assert sum(1 for v in LINK_RESULTS.values() if v == "Conforme") == 9


def test_address_plan_is_clean_and_draft_errors_found():
    assert PLAN_ERRORS == []
    net = ipaddress.IPv4Network("192.168.50.0/24")
    low, high = (ipaddress.IPv4Address(a) for a in POOL)
    for host in HOSTS:
        assert ipaddress.IPv4Address(host.ip) in net and host.prefix == 24
        if not host.dhcp:
            assert not low <= ipaddress.IPv4Address(host.ip) <= high, host.name
        else:
            assert low <= ipaddress.IPv4Address(host.ip) <= high, host.name
    assert len({h.ip for h in HOSTS}) == len(HOSTS)
    assert {e.split(" :")[0] for e in DRAFT_ERRORS} == {"IMP-01", "AP-01", "SW-01"}


def test_accounts_model_and_matrix_meet_needs():
    assert (MODEL, MODEL_LATER) == ("Groupe de travail", "Domaine Active Directory")
    expected = {
        "amartin": ("Modification", "Modification", "Aucun accès", "Aucun accès"),
        "cdubois": ("Modification", "Modification", "Lecture", "Lecture"),
        "flemaire": ("Modification", "Modification", "Aucun accès", "Modification"),
        "jroux": ("Modification", "Aucun accès", "Modification", "Aucun accès"),
        "nperrin": ("Modification", "Aucun accès", "Modification", "Aucun accès"),
        "tvidal": ("Modification", "Aucun accès", "Modification", "Aucun accès"),
    }
    assert {login: tuple(row[f] for f in FOLDERS) for login, row in MATRIX.items()} == expected
    assert STORED_ACCESS == "Aucun accès" and access("flemaire", "Compta") == "Modification"


def test_systems_wifi_and_security():
    assert OS_PLAN["LINUX1"].startswith("Ubuntu") and OS_PLAN["COMPTA"] == "Windows 11 Pro"
    assert AP_AUDIT == () and CHANNEL_24 in (1, 6, 11)
    strong_on = {n.channel for n in NEIGHBORS if n.dbm >= -80}
    assert CHANNEL_24 not in strong_on
    assert WORST_5 >= -67 and all(r[3] >= -67 for r in SURVEY_ROWS)
    assert len(PASSPHRASE_PRO) >= 20 and "lambert" not in PASSPHRASE_PRO.lower()
    assert all(32 <= ord(c) <= 126 for c in PASSPHRASE_PRO)  # clé WPA : ASCII imprimable
    kinds = [k for _t, k in SECURITY_ITEMS]
    assert len(set(kinds)) == 2 and "Masquer le nom du réseau Wi-Fi du personnel" in dict(SECURITY_ITEMS)


def test_recette_tree_and_final_verdict():
    assert RECETTE_DIAG["LINUX1"].startswith("Lien physique")
    assert RECETTE_DIAG["ETUDES2"].startswith("Adressage")
    assert RECETTE_DIAG["COMPTA"].startswith("Partage")
    assert [d for d in RECETTE_DIAG.values()].count("Réseau validé") == 3
    assert walk(RECETTE_TREE, (True, True, False))[0] == 3
    assert walk(RECETTE_TREE, (True,) * 6) == (None, RECETTE_TREE.final)
    assert FINAL_REPORT.verdict == V_RESERVE and FINAL_REPORT.decision == D_FOLLOWUP
    assert FINAL_REPORT.results.count(INCONCLUSIVE) == 1 and FINAL_REPORT.missing_checks == ()
    filled = FINAL_REPORT.filled()
    assert all(filled[f.key].strip() for f in REPORT_FIELDS)
    assert PASSPHRASE_PRO not in " ".join(filled.values()) + FINAL_REPORT.client_message


def test_eight_graded_cases_linked_to_official_requirements():
    assert [c.number for c in CASES] == list(range(1, 9))
    levels = [c.level for c in CASES]
    assert levels == sorted(levels) and set(levels) == {1, 2, 3, 4}
    covered = {r for c in CASES for r in c.official}
    assert {"AP-36", "AP-37", "AP-38"} <= covered
    for c in CASES:
        assert c.official and all(r in plan.REQUIREMENTS_BY_ID and not r.startswith("AP-C") for r in c.official)
        assert c.complements
    assert all(r not in covered for r in NOT_COVERED_OFFICIAL)
    assert {k for _t, k, _r in REQ_TASKS} == {"Exigence officielle (consignes, pp. 5-6)", "Complément pédagogique du parcours"}


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    figures = list(PR30_FIGURES) + [f for f, _p in STATIC_FIGURES]
    assert len({f.key for f in figures}) == len(figures)
    for figure in figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "non officiel" in html


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR30_FIGURES}
    assert by_key["pr30-plan-locaux"].svg.count('data-point="P') == LINKS
    assert by_key["pr30-recette-liens"].svg.count('data-result="Conforme"') == 9
    assert by_key["pr30-matrice-droits"].svg.count('data-cell="') == len(MATRIX) * len(FOLDERS)
    assert by_key["pr30-fiche-recette"].svg.count('data-diag="Réseau validé"') == 3
    assert by_key["pr30-arbre-recette"].svg.count('data-step="') == len(RECETTE_TREE.questions)
    assert by_key["pr30-couverture-wifi"].svg.count('data-dbm5="') == len(SURVEY_ROWS)
    assert by_key["pr30-baie"].svg.count('data-u="') == 7


def test_schemas_to_complete_hide_their_answers():
    rack, _p = STATIC_FIGURES[0]
    assert set(RACK_BLANK_ANSWERS) == {"①", "②", "③", "④"}
    for name in RACK_BLANK_ANSWERS.values():
        assert escape(name) not in rack.svg and name not in rack.alt, name
    tree, _p = STATIC_FIGURES[1]
    assert set(TREE_BLANK_ANSWERS) == {"①", "②", "③", "④"}
    for answer in TREE_BLANK_ANSWERS.values():
        first_words = " ".join(answer.split()[:3])
        assert escape(first_words) not in tree.svg and first_words not in tree.alt


def test_static_files_are_the_generated_content():
    for figure, path in STATIC_FIGURES:
        assert (STATIC_DIR / path).read_text(encoding="utf-8") == static_svg(figure), path


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 20 and len(EXAM_ITEMS) == 10  # ticket : ≥ 20 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_SCHEMA) == 2 and kinds.count(KIND_ORDER) == 2 and kinds.count(KIND_TREE) == 1
    assert kinds.count(KIND_WRITE) >= 1
    assert len(set(kinds)) >= 10  # transversaux : au moins dix thèmes du dossier
    assert {d.image for i in PRACTICE_ITEMS for d in i.documents if d.image} == {p for _f, p in STATIC_FIGURES}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        assert REQ & set(item.requirement_ids), item.key


def test_auto_corrected_answers():
    e05 = _item("E05")
    assert e05.classification.correct == E05_CORRECT
    assert [e05.classification.categories[c] for c in E05_CORRECT] == [
        "Conforme", "Défaut de câblage (continuité ou paires)", "Lien trop long",
        "Performances insuffisantes (certification échouée)", "Conforme", "Défaut de câblage (continuité ou paires)",
    ]
    assert [label for label, _t in E05_TESTS][2].startswith("Annexe")
    e16 = _item("E16")
    fakes = {e for e, c in zip(e16.classification.elements, e16.classification.correct, strict=True) if c == 1}
    assert "Considérer le miroir des deux disques du serveur comme la sauvegarde" in fakes
    assert "Noter la clé Wi-Fi et les mots de passe dans le rapport remis au client" in fakes
    for key in ("E04", "E18"):
        ordering = _item(key).ordering
        assert sorted(ordering.correct) == list(range(len(ordering.steps)))


def test_values_in_corrections_match_calculations():
    assert f"acheter {SWITCH_PORTS} ports" in _item("E02").criteria[1].expected
    assert "Canal 11" in _item("E15").criteria[0].expected
    assert "aucun accès" in _item("E12").criteria[0].expected
    assert "Groupe de travail" in _item("E10").criteria[0].expected
    assert f"switch de {X01_SWITCH} ports" in _item("X01").criteria[0].expected
    assert X01_SWITCH == 48 and X01_BOXES == 3 and sum(X01_LENGTHS) > 2 * 305
    assert "Lien trop long" in _item("X02").criteria[0].expected
    assert "doublon" in _item("X03").criteria[0].expected
    assert "Domaine Active Directory" in _item("X05").criteria[0].expected
    assert "non concluant" in _item("X09").criteria[0].expected


def test_schema_documents_point_to_static_files():
    layout = _document_layout(_item("E19").documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr30-baie-a-completer.svg"
    assert "non officiel" in layout["notice"]
    layout = _document_layout(_item("E20").documents[0])
    assert layout["src"] == "/static/img/ampcr-pratique/pr30-arbre-recette-a-completer.svg" and "①" in layout["alt"]


def test_no_bad_practice_presented_as_right():
    text = (_course_text() + " " + _all_items_text().lower()).replace("’", "'")
    for wrong in ("tout le monde : contrôle total » est correct", "masquer le ssid protège", "le miroir est une sauvegarde",
                  "on peut garder windows 10", "signer sans réserve malgré"):
        assert wrong not in text, wrong


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
# 4. Cours
# =============================================================================================


def test_eight_cases_procedures_and_exam_not_in_course():
    raw = _course_raw()
    text = _text(raw)
    for c in CASES:
        assert f"Cas {c.number} — {c.title} (niveau {c.level})" in text, c.number
    assert text.count("Variantes acceptées") == 8 and text.count("Corrigé.") == 8
    for i in (1, 2, 3, 4):
        assert f"Procédure {i} —" in text, i
    for item in EXAM_ITEMS:
        assert item.context not in raw and escape(item.context) not in raw, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in raw, item.key
    for figure in list(PR30_FIGURES) + [f for f, _p in STATIC_FIGURES]:
        assert f'id="fig-{figure.key}"' in raw, figure.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr30_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        "pme", "deux salles", "inventaire", "contraintes", "budget indicatif", "sans prix", "t568b", "baie",
        "plan ipv4", "dhcp", "dns", "comptes", "groupe de travail", "domaine", "droits", "installation",
        "windows 11 pro", "ubuntu", "panne matérielle", "panne logicielle", "wi-fi", "sécurité", "recette",
        "rapport", "plusieurs solutions", "variantes acceptées", "exigences officielles", "compléments",
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-36", "AP-37", "AP-38", "AP-C01", "AP-C02", "AP-C03"):
        assert req in text, req
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun cas n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    for link in ("/uaa/ampcr-mc15", "/uaa/ampcr-mc23", "/uaa/ampcr-mc25", "/uaa/ampcr-mc31",
                 "/uaa/ampcr-pratique-pr07", "/uaa/ampcr-pratique-pr08", "/uaa/ampcr-pratique-pr09",
                 "/uaa/ampcr-pratique-pr13", "/uaa/ampcr-pratique-pr15", "/uaa/ampcr-pratique-pr18",
                 "/uaa/ampcr-pratique-pr20", "/uaa/ampcr-pratique-pr22", "/uaa/ampcr-pratique-pr23",
                 "/uaa/ampcr-pratique-pr24", "/uaa/ampcr-pratique-pr25", "/uaa/ampcr-pratique-pr29",
                 f"/uaa/{PR30_SLUG}/practice", f"/uaa/{PR30_SLUG}/exam"):
        assert link in raw, link
    anchors = set(re.findall(r'id="(pr30-e\d\d)"', raw))
    assert anchors == {f"pr30-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert PASSPHRASE_PRO not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr30_course_sections()]
    assert kinds[:9] == ["theory"] * 9
    assert kinds[9:] == ["example", "example", "warning", "exercise", "exam", "summary", "info"]


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR30"]
    assert slot.ticket == 229 and slot.title == PR30_TITLE == PRACTICAL_COURSES_BY_CODE["PR30"].title
    assert slot.requirement_ids == ("AP-36", "AP-37", "AP-38")


# =============================================================================================
# 5. Seed, banque, correction
# =============================================================================================


def test_seed_publishes_pr30_in_practical_module_idempotently(db_session):
    module, uaa = _pr30(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR30_TITLE and uaa.position == 30
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR30").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr30_course_sections())
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR29") + 1 == ordered.index("PR30")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr30(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr30_specific():
    context = _pedagogical_context_for("PR30")
    assert context is get_practical_context("PR30")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("× 1,2", "jamais inventés", "T568B", "hors de l'étendue", "le plus restrictif",
                   "14 octobre 2025", "cmdkey", "WPS coupé", "n'est pas une sauvegarde", "premier échec"):
        assert notion in notions, notion
    assert "plusieurs solutions sont acceptées" in context.constraints and "prix inventé" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr30(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR30_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "\\\\SRV-01\\Compta" in _text(html)  # chemin UNC intact après le rendu Markdown
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200
    for linked in ("ampcr-mc15", "ampcr-pratique-pr18", "ampcr-pratique-pr20", "ampcr-pratique-pr25", "ampcr-pratique-pr29"):
        assert client.get(f"/uaa/{linked}").status_code == 200, linked


def test_practical_home_and_matrix_show_pr30(client, db_session):
    _pr30(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr30(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR30"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr30(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR30", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr30(db_session)
    for _ in range(3):  # 23 exercices : trois sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

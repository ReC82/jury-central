"""Ticket #201 — EX05 « Examen blanc global standard — épreuve pratique écrite ».

Contrôles : données des deux variantes recalculées indépendamment (module `ipaddress`,
formules écrites en dur), structure identique et données différentes, documents cités présents,
réponses absentes des énoncés, schémas sans verdict et fichiers statiques identiques, sujet sans
corrigé, seed idempotent après PR30, banque `exam` seule, contexte de correction propre, session
qui sert une variante entière dans l'ordre du sujet (variante 1 puis 2), corrigé masqué avant la
remise et note /100.
"""

import ipaddress
import re

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    get_practical_context,
    has_exam_variants,
    import_practical_bank,
    is_practical_exam_code,
    item_content,
    question_item_key,
    question_usage,
)
from app.v1.ampcr_pratique_ex05_bank import (
    ALL_ITEMS,
    DOMAINS,
    EXAM_ITEMS,
    PRACTICE_ITEMS,
    SITUATION_COURSES,
    VARIANT_ITEMS,
    VARIANT_KEYS,
    situation_of,
    validate_items,
)
from app.v1.ampcr_pratique_ex05_course import (
    EX05_SLUG,
    EX05_TITLE,
    evaluated_requirements,
    ex05_course_sections,
    missing_official_requirements,
)
from app.v1.ampcr_pratique_ex05_figures import (
    LAN_FIGURES,
    SCREEN_WIDTH,
    SMART_REPLACE,
    SMART_WATCH,
    STATIC_FIGURES,
    VARIANT_1,
    VARIANT_2,
    VARIANTS,
    screens,
    static_svg,
)
from app.v1.ampcr_pratique_visuals import T568B, render_figure, validate_figure
from app.v1.assets import STATIC_DIR
from app.v1.models import Question, QuestionnaireSession, SessionMode, User
from app.v1.prompt_layout import layout_for_item
from app.v1.question_engine import validate_content
from app.v1.session_service import EXAM_VARIANT_KEY, _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-ex05"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _subject_raw() -> str:
    return " ".join(c for _t, c in ex05_course_sections())


def _item(variant: int, situation: int):
    return VARIANT_ITEMS[variant][situation - 1]


def _stated(item) -> str:
    return " ".join((item.title, item.context, *item.instructions, *(d.content_text for d in item.documents)))


def _expected(item) -> str:
    return " ".join(c.expected for c in item.criteria) + " " + " ".join(item.correction)


def _ex05(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "EX05")
    return module, uaa


# =============================================================================================
# 1. Données des deux variantes, recontrôlées indépendamment
# =============================================================================================


def test_network_facts_with_ipaddress():
    for v, hosts in ((VARIANT_1, 254), (VARIANT_2, 510)):
        net = ipaddress.IPv4Network(v.network)
        f = v.facts
        assert (f.network, f.broadcast, f.mask, f.usable) == (
            str(net.network_address), str(net.broadcast_address), str(net.netmask), hosts)
        assert ipaddress.IPv4Address(v.box_ip) in net
        for low_high in v.pool:
            assert ipaddress.IPv4Address(low_high) in net
    assert VARIANT_2.facts.broadcast == "172.16.41.255"


def test_address_plan_errors_are_the_intended_ones():
    v1 = " | ".join(VARIANT_1.plan_errors)
    assert len(VARIANT_1.plan_errors) == 2
    assert "IMP-01" in v1 and "192.168.1.120" in v1 and "PC-06" in v1 and "/16" in v1
    v2 = " | ".join(VARIANT_2.plan_errors)
    assert len(VARIANT_2.plan_errors) == 3
    assert "PC-04" in v2 and "hors du réseau 172.16.41.0/24" in v2 and "PC-06" in v2 and "NAS-01" in v2
    # Recontrôle : la passerelle de PC-04 (/24) n'est pas dans son réseau ; le doublon existe.
    pc04 = VARIANT_2.host("PC-04")
    assert ipaddress.IPv4Address(pc04.gateway) not in ipaddress.IPv4Network(f"{pc04.ip}/24", strict=False)
    assert VARIANT_2.host("PC-06").ip == VARIANT_2.host("NAS-01").ip


def test_arp_table_reveals_the_duplicate_only_in_variant_2():
    v1 = "\n".join(screens(VARIANT_1)["arp"])
    v2 = "\n".join(screens(VARIANT_2)["arp"])
    assert "00-11-32-ab-00-10" in v1  # NAS-01 avec sa propre MAC
    assert "172.16.40.10       3c-52-82-22-01-06" in v2 and "00-11-32-cd-00-10" not in v2


def test_memory_upgrade_and_storage():
    assert (VARIANT_1.ram_after_gb, VARIANT_2.ram_after_gb) == (16, 16)
    assert VARIANT_1.ram_used_pct == round(100 * 7.4 / 7.9) == 94
    assert VARIANT_2.ram_used_pct == round(100 * 7.3 / 7.6) == 96
    assert "DDR4" in VARIANT_1.ram_type and "DIMM" in VARIANT_1.ram_type
    assert "DDR5" in VARIANT_2.ram_type and "SO-DIMM" in VARIANT_2.ram_type
    assert "HDD" in VARIANT_1.disk_label and VARIANT_1.disk_busy_pct == 100
    assert "SSD" in VARIANT_2.disk_label and VARIANT_2.disk_busy_pct < 50
    assert "Oui" in _item(1, 1).criteria[2].expected and "Non" in _item(2, 1).criteria[2].expected


def test_smart_verdicts():
    v1 = {r.post: r.verdict for r in VARIANT_1.smart}
    v2 = {r.post: r.verdict for r in VARIANT_2.smart}
    assert v1 == {"PC-02": SMART_REPLACE, "PC-04": "Sain"}
    assert v2 == {"PC-03": SMART_REPLACE, "NAS-01": SMART_WATCH}
    assert VARIANT_2.failing.reallocated == 0 and VARIANT_2.failing.pending > 0  # piège : pas de réalloué
    for v in VARIANTS:
        assert v.failing.post in {r.name for r in v.inventory}


def test_windows_firmware_and_activation():
    assert [c[0] for c in VARIANT_1.firmware_changes] == ["TPM 2.0 (Intel PTT / AMD fTPM)"]
    assert [c[0] for c in VARIANT_2.firmware_changes] == [
        "Mode de démarrage", "Démarrage sécurisé (Secure Boot)", "Mode du contrôleur SATA"]
    for v in VARIANTS:
        assert v.activation[0].startswith("S'active")
        assert "Oui, Windows s'activera" in _item(v.number, 3).criteria[2].expected


def test_linux_image_and_partitions():
    assert VARIANT_1.iso_verdict.startswith("Image intègre") and VARIANT_2.iso_verdict.startswith("Image corrompue")
    assert (VARIANT_1.swap_gb, VARIANT_2.swap_gb) == (8, 4)
    for v, home in ((VARIANT_1, 256 - 1 - 50 - 8), (VARIANT_2, 512 - 1 - 50 - 4)):
        assert v.linux_layout[-1][3] == f"le reste, environ {home} Go"
        assert [row[2] for row in v.linux_layout] == ["/boot/efi", "/", "[SWAP]", "/home"]


def test_rj45_tester_and_copper_run():
    assert T568B == ("blanc-orange", "orange", "blanc-vert", "bleu", "blanc-bleu", "vert", "blanc-marron", "marron")
    assert VARIANT_1.tester_faults == ["broche 1 arrive en 2", "broche 2 arrive en 1"]
    assert VARIANT_2.tester_faults == ["broche 7 ouverte (fil blanc-marron)"]
    assert (VARIANT_1.run_total_m, VARIANT_1.run_verdict) == (90, "Conforme")
    assert VARIANT_2.run_total_m == 103 and VARIANT_2.run_verdict.startswith("Trop long")
    assert VARIANT_2.run_permanent_m > 90


def test_coax_segment_readings():
    assert VARIANT_1.coax_reading == 50.0  # un seul terminateur vu
    assert abs(VARIANT_2.coax_reading - 50 * 75 / (50 + 75)) < 1e-9  # 30 Ω
    assert len(VARIANT_1.coax_errors) == 1 and "sans terminateur" in VARIANT_1.coax_errors[0]
    assert len(VARIANT_2.coax_errors) == 2 and any("RG-59" in e for e in VARIANT_2.coax_errors)
    for v in VARIANTS:
        assert v.coax_bus.length_m <= 185


def test_effective_access_matrices():
    assert VARIANT_1.access_matrix == {
        "Anne": {"Compta": "Lecture", "Clients": "Modification"},
        "Marc": {"Compta": "Lecture", "Clients": "Lecture"},
        "Julie": {"Compta": "Aucun accès", "Clients": "Modification"},
    }
    assert VARIANT_2.access_matrix == {
        "Paul": {"Etudes": "Modification", "Plans": "Modification"},
        "Sarah": {"Etudes": "Lecture", "Plans": "Modification"},
        "Léo": {"Etudes": "Lecture", "Plans": "Modification"},
    }
    assert (VARIANT_1.need_limiting_layer, VARIANT_2.need_limiting_layer) == ("partage", "NTFS")


def test_laptop_readings():
    v1 = [line for screen in VARIANT_1.laptop_screens for line in screen]
    v2 = [line for screen in VARIANT_2.laptop_screens for line in screen]
    assert "   Serveurs DNS . . . : 192.168.1.2" in v1 and any("n'a pas pu trouver" in line for line in v1)
    assert any("Réponse de 198.51.100.20" in line for line in v1)
    assert "   Passerelle défaut. :" in v2 and any("Défaillance générale" in line for line in v2)
    assert VARIANT_2.laptop.gateway is None and VARIANT_1.laptop.dns[0] != VARIANT_1.box_ip


def test_intervention_durations():
    assert (VARIANT_1.journal_minutes, VARIANT_2.journal_minutes) == (205, 245)
    assert "3 h 25" in _item(1, 10).criteria[1].expected and "4 h 05" in _item(2, 10).criteria[1].expected
    for v in VARIANTS:  # lignes contiguës
        assert all(a[1] == b[0] for a, b in zip(v.journal, v.journal[1:], strict=False))


def test_screens_fit_the_width():
    for v in VARIANTS:
        for name, lines in screens(v).items():
            assert all(len(line) <= SCREEN_WIDTH for line in lines), name


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_without_verdict():
    assert len(LAN_FIGURES) == 2
    for figure in LAN_FIGURES:
        assert validate_figure(figure) == []
        html = str(render_figure(figure))
        assert 'role="img"' in html
        lowered = figure.svg.lower()
        for word in ("✓", "✗", "erreur", "faux", "conforme", "doublon"):
            assert word not in lowered


def test_static_figure_files_are_the_generated_svg():
    assert len(STATIC_FIGURES) == 2
    for figure, path in STATIC_FIGURES:
        content = (STATIC_DIR / path).read_text()
        assert content == static_svg(figure)
        assert content.startswith("<svg ") and "<title>" in content


def test_schema_shows_every_host_configuration():
    for v, (figure, _path) in zip(VARIANTS, STATIC_FIGURES, strict=True):
        for host in v.hosts[1:]:
            assert host.ip in figure.svg and host.mask in figure.svg and host.name in figure.svg


# =============================================================================================
# 3. Questions
# =============================================================================================


def test_items_valid_and_scored_on_100_per_variant():
    assert validate_items() == []
    assert len(ALL_ITEMS) == len(EXAM_ITEMS) == 20 and PRACTICE_ITEMS == ()
    for v in VARIANTS:
        items = VARIANT_ITEMS[v.number]
        assert [situation_of(i) for i in items] == list(range(1, 11))
        assert sum(i.total_points for i in items) == 100
        assert all(len(i.criteria) == 4 for i in items)
    assert sum(10 * len(nums) for _n, nums in DOMAINS) == 100
    assert sorted(n for _n, nums in DOMAINS for n in nums) == list(range(1, 11))
    assert set(SITUATION_COURSES) == set(range(1, 11))


def test_variants_share_structure_but_not_data():
    for a, b in zip(VARIANT_ITEMS[1], VARIANT_ITEMS[2], strict=True):
        assert a.title == b.title and a.requirement_ids == b.requirement_ids
        assert [c.label for c in a.criteria] == [c.label for c in b.criteria]
        assert [c.points for c in a.criteria] == [c.points for c in b.criteria]
        assert a.prompt != b.prompt and _expected(a) != _expected(b)
    assert VARIANT_KEYS == tuple(tuple(i.key for i in VARIANT_ITEMS[v.number]) for v in VARIANTS)
    assert len({i.prompt for i in EXAM_ITEMS}) == 20


def test_ticket_subjects_are_all_covered():
    text = " ".join(_stated(i) + " " + _expected(i) for i in VARIANT_ITEMS[1]).lower()
    for subject in ("6 postes", "schéma", "inventaire", "journal", "windows 11", "ubuntu", "partag", "rj45",
                    "bnc", "adresse", "diagnostic", "rapport"):
        assert subject in text, subject


def test_items_cover_the_slot_requirements_and_list_gaps():
    slot = plan.EXERCISE_SLOTS_BY_CODE["EX05"]
    assert set(slot.requirement_ids) <= set(evaluated_requirements())
    missing = set(missing_official_requirements())
    assert missing and not missing & set(evaluated_requirements())
    assert {"AP-23", "AP-33"} <= missing  # topologies et Wi-Fi : évalués par EX04, pas ici


def test_cited_documents_are_given_with_the_question():
    for item in EXAM_ITEMS:
        numbers = {int(n) for n in re.findall(r"documents? (\d+)", " ".join((item.context, *item.instructions)))}
        given = {int(re.search(r"document (\d+) —", d.title).group(1)) for d in item.documents}
        assert numbers <= given, (item.key, numbers, given)
        assert all(d.title.startswith(item.context.split(".")[0]) for d in item.documents)


def test_answers_are_not_given_in_the_statements():
    for v in VARIANTS:
        n = v.number
        assert "25 Ω" not in _stated(_item(n, 6))
        assert SMART_REPLACE not in _stated(_item(n, 2)) and SMART_WATCH not in _stated(_item(n, 2))
        assert v.facts.broadcast not in _stated(_item(n, 7))
        assert "Défaillance générale :" not in _stated(_item(n, 9))
        assert str(v.journal_minutes) not in _stated(_item(n, 10))
        for item in VARIANT_ITEMS[n]:
            assert "officiel" not in item.title.lower()
    assert "AHCI" not in _stated(_item(2, 3)).replace("Mode du contrôleur SATA", "")


def test_items_content_matches_existing_question_types():
    for item in EXAM_ITEMS:
        content = item_content(item, list(range(1, len(item.documents) + 1)))
        validate_content(item.question_type, 1, content)
        assert "Barème" in content["rubric"] and content["max_score"] == 10


def test_prompt_layout_shows_the_variant_label():
    layout = layout_for_item("EX05", _item(2, 4))
    assert layout.label == "Variante 2" and not layout.context.startswith("Variante")
    assert len(layout.steps) == 4


# =============================================================================================
# 4. Sujet (version candidat)
# =============================================================================================


def test_subject_has_both_variants_without_corrections():
    raw = _subject_raw()
    for item in EXAM_ITEMS:
        assert f"Question {situation_of(item)} — " in raw
        for step in item.correction:
            assert step[:60] not in raw
        for criterion in item.criteria:
            assert criterion.expected[:60] not in raw
    assert raw.count('class="jc-ex-answer"') == 20 and raw.count('class="jc-ex-dossier"') == 2
    assert "Corrigé de référence" not in raw and "<details" not in raw
    for v in VARIANTS:
        for n in range(1, 11):
            assert f'id="ex05-v{v.number}-q{n}"' in raw


def test_subject_presents_scoring_variants_and_sources():
    text = _text(_subject_raw()).replace("**", "")
    assert "10 situations à réponse rédigée" in text and "sur 100" in text
    assert "pas la durée officielle" in text and "fictives" in text and "deux variantes" in text
    assert "/uaa/ampcr-pratique-ex05/exam" in text and "Ctrl + P" in text
    assert "Non évaluées dans cet examen blanc" in text
    for code in plan.EXERCISE_SLOTS_BY_CODE["EX05"].requirement_ids:
        assert code in text
    for name, _nums in DOMAINS:
        assert name in text


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(title) for title, _c in ex05_course_sections()]
    assert kinds == ["theory"] * 7 + ["method", "info"]


# =============================================================================================
# 5. Banque, seed, pages, sessions
# =============================================================================================


def test_seed_publishes_ex05_after_pr30_idempotently(db_session):
    module, uaa = _ex05(db_session)
    assert uaa.slug == SLUG == EX05_SLUG and uaa.is_published and uaa.title == EX05_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="EX05").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(ex05_course_sections())
    from app.v1.parcours import listed_uaas

    codes = [u.code for u in listed_uaas(db_session.get(Module, module.id))]
    assert codes.index("EX05") == codes.index("PR30") + 1
    assert codes.index("EX04") == codes.index("PR25") + 1
    assert {"EX01", "EX02", "EX03", "EX04", "EX05"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_exam_reserve_only(db_session):
    module, uaa = _ex05(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert is_practical_exam_code("EX05") and has_exam_variants("EX05") and not has_exam_variants("EX04")
    assert import_practical_bank(db_session, module, uaa) == 20
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert [question_usage(q) for q in questions] == ["exam"] * 20
    course = PRACTICAL_COURSES_BY_CODE["EX05"]
    assert sorted(question_item_key(q, course) for q in questions) == sorted(i.key for i in EXAM_ITEMS)


def test_correction_context_is_ex05_specific():
    context = _pedagogical_context_for("EX05")
    assert context is get_practical_context("EX05") and context.course_key == SLUG
    assert context is not get_practical_context("EX04")
    notions = " ".join(context.allowed_notions)
    assert "SMART" in notions and "T568B" in notions and "RG-58" in notions and "NTFS" in notions
    assert "/100" in context.level and "mot-clé" in context.constraints


def test_subject_page_navigation_and_home(client, db_session):
    _ex05(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    assert f'href="/uaa/{SLUG}/practice"' not in html and f"/uaa/{SLUG}/exam" in html
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in LAN_FIGURES}
    assert html.count('class="jc-ex-question"') == 20
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus\s+· \d examens blancs sur 6", home)  # EX06 (#234) publié ensuite
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200


def test_practice_redirects_to_exam(authenticated_client, db_session):
    _ex05(db_session)
    response = authenticated_client.get(f"/uaa/{SLUG}/practice", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == f"/uaa/{SLUG}/exam"
    assert db_session.query(QuestionnaireSession).count() == 0


def _session_keys(db_session, session) -> list[str]:
    course = PRACTICAL_COURSES_BY_CODE["EX05"]
    ordered = sorted(session.session_questions, key=lambda sq: sq.position)
    return [question_item_key(sq.question_version.question, course) for sq in ordered]


def test_exam_sessions_serve_whole_variants_in_order(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _ex05(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="EX05", mode=SessionMode.EXAM
    ) == (10,)

    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert session.question_count == 10 and fake.questionnaire_calls == []
    assert _session_keys(db_session, session) == list(VARIANT_KEYS[0])
    assert session.parameters_json[EXAM_VARIANT_KEY] == 1
    shown = set()
    for position in range(1, 11):
        page = authenticated_client.get(f"{session_url}?q={position}").text
        assert "Corrigé de référence" not in page and "Barème" not in page
        assert "Variante 1" in page
        shown |= {path for _f, path in STATIC_FIGURES if path in page}
    assert shown == {STATIC_FIGURES[0][1]}  # le schéma de la variante 1, dans la question 7
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-100" in html and "/ 100" in html

    second_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    assert second_url != session_url
    second = db_session.get(QuestionnaireSession, int(second_url.rsplit("/", 1)[-1]))
    assert _session_keys(db_session, second) == list(VARIANT_KEYS[1])
    assert second.parameters_json[EXAM_VARIANT_KEY] == 2

"""Ticket #234 — EX06 « Examen blanc global avancé — dossiers complexes ».

Contrôles : données des deux variantes recalculées indépendamment (module `ipaddress`,
formules et valeurs écrites en dur), plusieurs causes départagées dans chaque dossier,
structure identique et données différentes, documents cités présents, réponses absentes des
énoncés, schémas sans verdict et fichiers statiques identiques, sujet sans corrigé, couverture
comparée avec EX05, seed idempotent après EX05, banque `exam` seule, contexte de correction
propre, longueur fixée à 12, sessions qui servent une variante entière dans l'ordre du sujet
(variante 1 puis 2), corrigé masqué avant la remise et note /100.
"""

import ipaddress
import math
import re

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    exam_variant_length,
    get_practical_context,
    has_exam_variants,
    import_practical_bank,
    is_practical_exam_code,
    item_content,
    question_item_key,
    question_usage,
)
from app.v1.ampcr_pratique_ex05_bank import EXAM_ITEMS as EX05_ITEMS
from app.v1.ampcr_pratique_ex06_bank import (
    ALL_ITEMS,
    DOSSIERS,
    EX05_COMPARISON,
    EXAM_ITEMS,
    PRACTICE_ITEMS,
    SITUATION_COURSES,
    SITUATION_POINTS,
    VARIANT_ITEMS,
    VARIANT_KEYS,
    situation_of,
    validate_items,
)
from app.v1.ampcr_pratique_ex06_course import (
    EX06_SLUG,
    EX06_TITLE,
    evaluated_requirements,
    ex06_course_sections,
    missing_official_requirements,
)
from app.v1.ampcr_pratique_ex06_figures import (
    CAUSE_CONTROLLER,
    CAUSE_DISK_DEAD,
    LAN_FIGURES,
    SCREEN_WIDTH,
    SPEED_100,
    SPEED_1000,
    STATIC_FIGURES,
    VARIANT_1,
    VARIANT_2,
    VARIANTS,
    WIFI_FIGURES,
    screens,
    static_svg,
)
from app.v1.ampcr_pratique_pr23_figures import (
    LEVEL_MODIFY,
    LEVEL_NONE,
    LEVEL_READ,
    Ace,
    Share,
    effective_access,
)
from app.v1.ampcr_pratique_visuals import render_figure, validate_figure
from app.v1.assets import STATIC_DIR
from app.v1.models import Question, QuestionnaireSession, SessionMode, User
from app.v1.prompt_layout import layout_for_item
from app.v1.question_engine import validate_content
from app.v1.session_service import (
    EXAM_VARIANT_KEY,
    _pedagogical_context_for,
    available_session_lengths,
    session_length_options,
)
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-ex06"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _subject_raw() -> str:
    return " ".join(c for _t, c in ex06_course_sections())


def _item(variant: int, situation: int):
    return VARIANT_ITEMS[variant][situation - 1]


def _stated(item) -> str:
    return " ".join((item.title, item.context, *item.instructions, *(d.content_text for d in item.documents)))


def _expected(item) -> str:
    return " ".join(c.expected for c in item.criteria) + " " + " ".join(item.correction)


def _ex06(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "EX06")
    return module, uaa


# =============================================================================================
# 1. Données des deux variantes, recontrôlées indépendamment
# =============================================================================================


def test_dossier_a_boot_causes_are_discriminated():
    b1, b2 = VARIANT_1.boot, VARIANT_2.boot
    # Variante 1 : disque vu, SMART bon, contrôleur changé depuis l'installation.
    assert b1.disk_in_firmware and b1.smart_status == "Bon" and b1.controller_now != b1.controller_install
    assert b1.cause == CAUSE_CONTROLLER and not b1.battery_worn
    # Variante 2 : disque invisible partout (autre câble, autre PC) ; pile usée, indice secondaire.
    assert not b2.disk_in_firmware and b2.disk_seen_other_cable is False and b2.disk_seen_other_pc is False
    assert b2.cause == CAUSE_DISK_DEAD and b2.battery_worn and b2.battery_v < 3.0


def test_dossier_a_storage_units_and_filesystems():
    assert round(4 * 10**12 / 2**40, 2) == VARIANT_1.new_disk_shown_tib == 3.64
    assert round(2 * 10**12 / 2**40, 2) == VARIANT_2.new_disk_shown_tib == 1.82
    assert VARIANT_1.new_disk_mbr_lost_tib == round((4 * 10**12 - 2**32 * 512) / 2**40, 2) == 1.64
    assert VARIANT_2.new_disk_mbr_lost_tib == 0  # 2 To < 2 Tio
    assert VARIANT_1.new_disk_table == VARIANT_2.new_disk_table == "GPT"
    assert (VARIANT_1.new_disk_fs, VARIANT_1.removable_fs) == ("NTFS", "exFAT")  # 6,4 Gio > 4 Gio
    assert (VARIANT_2.new_disk_fs, VARIANT_2.removable_fs) == ("NTFS", "FAT32")  # 0,35 Gio, appareil ancien
    assert VARIANT_1.removable_largest[1] > 4 > VARIANT_2.removable_largest[1]


def test_dossier_a_data_protection():
    assert len(VARIANT_1.missing_321) == 3
    assert VARIANT_2.missing_321 == ("moins de 3 copies", "un seul type de support")
    assert VARIANT_1.copy_check == ((), ("Concours-ecole-maquette.skp",))
    assert VARIANT_2.copy_check == (("Charte-client-Brasserie.ai",), ())
    assert len(VARIANT_1.data_prerequisites) == 3  # effacement : pas de remise en service
    assert any("licences" in p for p in VARIANT_2.data_prerequisites)


def test_dossier_b_quote_and_power_budget():
    assert VARIANT_1.quote_failures == ["Mémoire ↔ carte", "Ventirad ↔ boîtier et socket", "Bloc : puissance"]
    assert VARIANT_2.quote_failures == ["Processeur ↔ socket", "Carte mère ↔ boîtier", "Carte graphique ↔ boîtier",
                                        "Bloc : connecteurs PCIe"]
    for v, total, psu in ((VARIANT_1, 533, 750), (VARIANT_2, 464, 700)):
        assert v.budget_w == sum(load.watts for load in v.loads) == total
        palier = math.ceil(total * 1.3 / 50) * 50
        assert v.psu_w == max(palier, v.quote.gpu_psu_recommendation_w) == psu
    assert VARIANT_1.quote.psu_watts < VARIANT_1.psu_w and VARIANT_2.quote.psu_watts >= VARIANT_2.psu_w


def test_dossier_b_windows_and_linux():
    assert VARIANT_1.activation[0].startswith("Ne s'active pas")  # Famille installée, licence Pro
    assert VARIANT_2.activation[0].startswith("S'active")
    assert (VARIANT_1.swap_gb, VARIANT_2.swap_gb) == (4, 8)
    assert VARIANT_1.iso_verdict.startswith("Image intègre") and VARIANT_2.iso_verdict.startswith("Image corrompue")
    actions_1 = dict(VARIANT_1.dual_boot_plan)
    assert actions_1["ESP (FAT32, 100 Mo)"].startswith("Réutiliser sans formater")
    assert actions_1["Windows C: (NTFS)"] == "Ne pas toucher"
    assert all(a.startswith("Arrêter") for _z, a in VARIANT_2.dual_boot_plan)  # ni copie relue ni accord écrit
    assert VARIANT_1.first_boot == VARIANT_2.first_boot == "Windows Boot Manager"
    assert "ubuntu" in " ".join(VARIANT_1.efibootmgr) and "ubuntu" not in " ".join(VARIANT_2.efibootmgr)


def test_dossier_c_cord_and_coax():
    assert VARIANT_1.cord_speed == SPEED_100 and VARIANT_1.cord_faults == ["broche 8 ouverte (fil marron)"]
    assert VARIANT_2.cord_speed == SPEED_1000 and VARIANT_2.cord_faults == []  # le testeur ne voit rien
    assert VARIANT_2.cord_split == [(3, 6), (4, 5)] and VARIANT_2.cord_next_fail
    # Variante 1 : 25 Ω (2 × 50 Ω en parallèle) ; dérivation et 192 m > 185 m.
    assert [r for _n, r in VARIANT_1.coax_readings] == [50 * 50 / (50 + 50)] * 2
    assert VARIANT_1.coax_bus.length_m == 64 + 71 + 57 == 192
    assert len(VARIANT_1.coax_errors) == 2
    # Variante 2 : coupure → 50 Ω à chaque T.
    assert [r for _n, r in VARIANT_2.coax_readings] == [50.0] * 4
    assert VARIANT_2.coax_errors == ["Tronçon de 22 m : câble coupé."]


def test_dossier_d_network_growth_with_ipaddress():
    for v, prefix, broadcast, hosts in ((VARIANT_1, 24, "192.168.50.255", 254), (VARIANT_2, 23, "10.20.1.255", 510)):
        net = ipaddress.IPv4Network(f"{v.box.ip}/{prefix}", strict=False)
        assert v.new_prefix == prefix and v.new_facts.broadcast == str(net.broadcast_address) == broadcast
        assert v.new_facts.usable == net.num_addresses - 2 == hosts >= v.needed_addresses
        smaller = ipaddress.IPv4Network(f"{v.box.ip}/{prefix + 1}", strict=False)
        assert smaller.num_addresses - 2 < v.needed_addresses
        low, high = (ipaddress.IPv4Address(a) for a in v.new_pool)
        assert low in net and high in net
    assert VARIANT_1.pool_size == 57 and VARIANT_2.pool_size == 101
    errors_1 = " ".join(VARIANT_1.new_plan_errors)
    assert "APIPA" in errors_1 and "IMP-02" in errors_1 and "PC-DIR" not in errors_1
    errors_2 = " ".join(VARIANT_2.new_plan_errors)
    assert "PC-11 : masque" in errors_2 and "PC-PAO : passerelle" in errors_2 and "IMP-01" not in errors_2


def _dbm(distance: float, freq: int, loss: int) -> int:
    return round(20 - (20 * math.log10(distance) + 20 * math.log10(freq) - 27.55) - loss)


def test_dossier_d_wifi_recomputed():
    # Pertes (2,4 / 5 GHz) : vitre 2/3, cloison 3/4, brique 6/10, béton 12/18, dalle 15/25, métal 20/25.
    loss = {"vitre": (2, 3), "cloison": (3, 4), "brique": (6, 10), "béton": (12, 18), "dalle": (15, 25),
            "métal": (20, 25)}
    for v in VARIANTS:
        for point, (key, a, _sa, b, _sb) in zip(v.wifi_points, v.wifi_table, strict=True):
            assert key == point.key
            assert a == _dbm(point.distance_m, 2437, sum(loss[o][0] for o in point.obstacles))
            assert b == _dbm(point.distance_m, 5180, sum(loss[o][1] for o in point.obstacles))
    assert VARIANT_1.best_channel == 11 and VARIANT_2.best_channel == 1
    assert [p for p, _f in VARIANT_1.ap_audit][:3] == ["Sécurité", "Clé", "WPS"]
    assert {"Sécurité", "SSID masqué", "DHCP", "Largeur 2,4 GHz"} <= {p for p, _f in VARIANT_2.ap_audit}
    for v in VARIANTS:
        assert v.extension.wired_mbps == 2 * v.extension.repeater_mbps  # répéteur : débit divisé par deux


def test_dossier_d_effective_access_written_out():
    root = "D:\\Partages\\"
    assert VARIANT_1.access_matrix == {
        "cmorel": {root + "Projets": LEVEL_MODIFY, root + "Projets\\Concours": LEVEL_MODIFY,
                   root + "Projets\\Chantiers": LEVEL_MODIFY},
        "hdubois": {root + "Projets": LEVEL_MODIFY, root + "Projets\\Concours": LEVEL_NONE,
                    root + "Projets\\Chantiers": LEVEL_MODIFY},
        "ilambert": {root + "Projets": LEVEL_READ, root + "Projets\\Concours": LEVEL_NONE,
                     root + "Projets\\Chantiers": LEVEL_NONE},
    }
    assert VARIANT_1.need_limiting_layer == "NTFS"
    assert VARIANT_2.need_limiting_layer == "partage"
    assert VARIANT_2.access("kbenali", root + "Production", remote=False) == LEVEL_MODIFY  # sur le serveur
    # Correction proposée en variante 2 : partage « Utilisateurs authentifiés : Modifier ».
    fixed = {"Production": Share("Production", root + "Production", (Ace("Utilisateurs authentifiés", "Modifier"),
                                                                       Ace("G_Direction", "Contrôle total")))}

    def after(login: str, path: str) -> str:
        return effective_access(VARIANT_2.account(login), root + path, tree=VARIANT_2.share_tree, shares=fixed)

    assert after("kbenali", "Production") == LEVEL_MODIFY
    assert after("mdufour", "Production") == LEVEL_READ and after("mdufour", "Production\\Tarifs") == LEVEL_MODIFY
    assert after("lpetit", "Production\\BAT") == LEVEL_MODIFY and after("lpetit", "Production\\Tarifs") == LEVEL_READ


def test_dossier_d_journal_durations():
    assert (VARIANT_1.journal_minutes, VARIANT_1.journal_span) == (50 + 45 + 100 + 45 + 55 + 90, 430) == (385, 430)
    assert (VARIANT_2.journal_minutes, VARIANT_2.journal_span) == (405, 455)


def test_screens_fit_the_width():
    for v in VARIANTS:
        for name, lines in screens(v).items():
            assert all(len(line) <= SCREEN_WIDTH for line in lines), (name, [x for x in lines if len(x) > SCREEN_WIDTH])


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_without_verdict():
    assert len(LAN_FIGURES) == len(WIFI_FIGURES) == 2
    for figure in (*LAN_FIGURES, *WIFI_FIGURES):
        assert validate_figure(figure) == []
        assert 'role="img"' in str(render_figure(figure))
        lowered = figure.svg.lower()
        for word in ("✓", "✗", "erreur", "faux", "conforme", "doublon", "excellent", "insuffisant"):
            assert word not in lowered, (figure.key, word)
        assert not re.search(r"[-−]\d+ ?dbm", lowered)  # aucun signal reçu : il est à calculer


def test_static_figure_files_are_the_generated_svg():
    assert len(STATIC_FIGURES) == 4
    for figure, path in STATIC_FIGURES:
        content = (STATIC_DIR / path).read_text()
        assert content == static_svg(figure) and content.startswith("<svg ") and "<title>" in content


def test_schemas_show_every_host_and_survey_point():
    for v, lan, wifi in zip(VARIANTS, LAN_FIGURES, WIFI_FIGURES, strict=True):
        for host in v.hosts[1:]:
            assert host.name in lan.svg and (host.ip == "DHCP" or (host.ip in lan.svg and host.mask in lan.svg))
        for point in v.wifi_points:
            assert point.place in wifi.svg and f"{point.distance_m:g} m" in wifi.svg


# =============================================================================================
# 3. Questions
# =============================================================================================


def test_items_valid_and_scored_on_100_per_variant():
    assert validate_items() == []
    assert len(ALL_ITEMS) == len(EXAM_ITEMS) == 24 and PRACTICE_ITEMS == ()
    for v in VARIANTS:
        items = VARIANT_ITEMS[v.number]
        assert [situation_of(i) for i in items] == list(range(1, 13))
        assert sum(i.total_points for i in items) == 100
        assert all(len(i.criteria) == 4 for i in items)
        assert [i.total_points for i in items] == [SITUATION_POINTS[n] for n in range(1, 13)]
    assert sorted(n for _l, _t, nums in DOSSIERS for n in nums) == list(range(1, 13))
    assert len(DOSSIERS) == 4 and set(SITUATION_COURSES) == set(EX05_COMPARISON) == set(range(1, 13))


def test_variants_share_structure_but_not_data():
    for a, b in zip(VARIANT_ITEMS[1], VARIANT_ITEMS[2], strict=True):
        assert a.title == b.title and a.requirement_ids == b.requirement_ids
        assert [(c.label, c.points) for c in a.criteria] == [(c.label, c.points) for c in b.criteria]
        assert a.prompt != b.prompt and _expected(a) != _expected(b)
    assert VARIANT_KEYS == tuple(tuple(i.key for i in VARIANT_ITEMS[v.number]) for v in VARIANTS)
    assert len({i.prompt for i in EXAM_ITEMS}) == 24


def test_no_question_duplicated_from_ex05():
    ex05_titles = {i.title for i in EX05_ITEMS}
    assert not ex05_titles & {i.title for i in EXAM_ITEMS}
    assert not {i.prompt for i in EX05_ITEMS} & {i.prompt for i in EXAM_ITEMS}


def test_ticket_subjects_are_all_covered():
    text = " ".join(_stated(i) + " " + _expected(i) for i in VARIANT_ITEMS[1]).lower()
    for subject in ("ne démarre plus", "stockage", "incompatib", "windows 11", "ubuntu", "rj45", "bnc", "masque",
                    "wi-fi", "partage", "rapport", "calcul", "test", "sauvegarde", "faux indice"):
        assert subject in text, subject


def test_items_cover_the_slot_requirements_and_list_gaps():
    slot = plan.EXERCISE_SLOTS_BY_CODE["EX06"]
    assert set(slot.requirement_ids) <= set(evaluated_requirements())
    missing = set(missing_official_requirements())
    assert missing and not missing & set(evaluated_requirements())


def test_cited_documents_are_given_with_the_question():
    for item in EXAM_ITEMS:
        cited = " ".join((item.context, *item.instructions))
        numbers = {int(n) for n in re.findall(r"documents? (\d+)", cited)}
        numbers |= {int(n) for n in re.findall(r"documents \d+ et (\d+)", cited)}
        given = {int(re.search(r"document (\d+) —", d.title).group(1)) for d in item.documents}
        assert numbers <= given, (item.key, numbers, given)
        assert all(d.title.startswith(item.context.split(".")[0]) for d in item.documents)


def test_answers_are_not_given_in_the_statements():
    for v in VARIANTS:
        n = v.number
        assert v.boot.cause not in _stated(_item(n, 1))
        assert v.new_disk_table not in _stated(_item(n, 2))
        assert str(v.psu_w) + " W" not in _stated(_item(n, 4)).replace(
            f"recommandée {v.quote.gpu_psu_recommendation_w} W", "")
        assert v.new_facts.broadcast not in _stated(_item(n, 9)) and f"/{v.new_prefix}" not in _stated(_item(n, 9))
        assert str(v.journal_minutes) not in _stated(_item(n, 12))
        assert "dBm en 2,4 GHz" not in _stated(_item(n, 10))
        for item in VARIANT_ITEMS[n]:
            assert "officiel" not in item.title.lower()
    assert "exFAT" not in _stated(_item(1, 2))  # variante 2 : l'appareil « lit seulement FAT32 » (donnée)
    assert "paires séparées" not in _stated(_item(2, 7))
    assert "VMD" not in _stated(_item(1, 5)).replace("contrôleur Intel VMD activé", "")


def test_items_content_matches_existing_question_types():
    for item in EXAM_ITEMS:
        content = item_content(item, list(range(1, len(item.documents) + 1)))
        validate_content(item.question_type, 1, content)
        assert "Barème" in content["rubric"] and content["max_score"] == SITUATION_POINTS[situation_of(item)]


def test_prompt_layout_shows_the_variant_label():
    layout = layout_for_item("EX06", _item(2, 6))
    assert layout.label == "Variante 2" and layout.context.startswith("Dossier B")
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
    assert raw.count('class="jc-ex-answer"') == 24 and raw.count('class="jc-ex-dossier"') == 2
    assert "Corrigé de référence" not in raw and "<details" not in raw
    for v in VARIANTS:
        for n in range(1, 13):
            assert f'id="ex06-v{v.number}-q{n}"' in raw
    for figure in (*LAN_FIGURES, *WIFI_FIGURES):
        assert f'id="fig-{figure.key}"' in raw


def test_subject_presents_scoring_comparison_and_sources():
    text = _text(_subject_raw()).replace("**", "")
    assert "12 situations à réponse rédigée" in text and "sur 100" in text
    assert "pas la durée officielle" in text and "fictives" in text and "deux variantes" in text
    assert "Couverture comparée avec EX05" in text and "Aucune question d'EX05 n'est reprise" in text
    assert "/uaa/ampcr-pratique-ex06/exam" in text and "Ctrl + P" in text
    assert "Non évaluées dans cet examen blanc" in text
    for code in plan.EXERCISE_SLOTS_BY_CODE["EX06"].requirement_ids:
        assert code in text
    for letter, title, _nums in DOSSIERS:
        assert f"Dossier {letter} — {title}" in text


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(title) for title, _c in ex06_course_sections()]
    assert kinds == ["theory"] * 11 + ["method", "info"]


# =============================================================================================
# 5. Banque, seed, pages, sessions
# =============================================================================================


def test_seed_publishes_ex06_after_ex05_idempotently(db_session):
    module, uaa = _ex06(db_session)
    assert uaa.slug == SLUG == EX06_SLUG and uaa.is_published and uaa.title == EX06_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="EX06").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(ex06_course_sections())
    from app.v1.parcours import listed_uaas

    codes = [u.code for u in listed_uaas(db_session.get(Module, module.id))]
    assert codes.index("EX06") == codes.index("EX05") + 1 == codes.index("PR30") + 2
    assert {"EX01", "EX02", "EX03", "EX04", "EX05", "EX06"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_exam_reserve_only(db_session):
    module, uaa = _ex06(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert is_practical_exam_code("EX06") and has_exam_variants("EX06")
    assert exam_variant_length("EX06") == 12 and exam_variant_length("EX05") == 10
    assert exam_variant_length("EX04") is None
    assert import_practical_bank(db_session, module, uaa) == 24
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert [question_usage(q) for q in questions] == ["exam"] * 24
    course = PRACTICAL_COURSES_BY_CODE["EX06"]
    assert sorted(question_item_key(q, course) for q in questions) == sorted(i.key for i in EXAM_ITEMS)


def test_correction_context_is_ex06_specific():
    context = _pedagogical_context_for("EX06")
    assert context is get_practical_context("EX06") and context.course_key == SLUG
    assert context is not get_practical_context("EX05")
    notions = " ".join(context.allowed_notions)
    for notion in ("INACCESSIBLE_BOOT_DEVICE", "3-2-1", "mbr2gpt", "paires séparées", "25 Ω", "APIPA", "WPA3",
                   "refus explicite"):
        assert notion in notions, notion
    assert "/100" in context.level and "mot-clé" in context.constraints


def test_session_length_options_follow_the_variant():
    assert session_length_options(uaa_id=1, uaa_code="EX06") == (12,)
    assert session_length_options(uaa_id=1, uaa_code="EX05") == (10,)
    assert session_length_options(uaa_id=1, uaa_code="EX04") == (10, 20, 30, 40)


def test_subject_page_navigation_and_home(client, db_session):
    _ex06(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    assert f'href="/uaa/{SLUG}/practice"' not in html and f"/uaa/{SLUG}/exam" in html
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in (*LAN_FIGURES, *WIFI_FIGURES)}
    assert html.count('class="jc-ex-question"') == 24
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus\s+· 6 examens blancs sur 6", home)
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200


def test_practice_redirects_to_exam(authenticated_client, db_session):
    _ex06(db_session)
    response = authenticated_client.get(f"/uaa/{SLUG}/practice", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == f"/uaa/{SLUG}/exam"
    assert db_session.query(QuestionnaireSession).count() == 0


def _session_keys(session) -> list[str]:
    course = PRACTICAL_COURSES_BY_CODE["EX06"]
    ordered = sorted(session.session_questions, key=lambda sq: sq.position)
    return [question_item_key(sq.question_version.question, course) for sq in ordered]


def test_exam_sessions_serve_whole_variants_in_order(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _ex06(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="EX06", mode=SessionMode.EXAM
    ) == (12,)
    start = authenticated_client.get(f"/uaa/{SLUG}/exam").text
    assert 'id="question-count-12"' in start and 'id="question-count-10"' not in start

    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert session.question_count == 12 and fake.questionnaire_calls == []
    assert _session_keys(session) == list(VARIANT_KEYS[0])
    assert session.parameters_json[EXAM_VARIANT_KEY] == 1
    shown = set()
    for position in range(1, 13):
        page = authenticated_client.get(f"{session_url}?q={position}").text
        assert "Corrigé de référence" not in page and "Barème" not in page
        assert "Variante 1" in page
        shown |= {path for _f, path in STATIC_FIGURES if path in page}
    assert shown == {STATIC_FIGURES[0][1], STATIC_FIGURES[2][1]}  # réseau (Q9) et Wi-Fi (Q10) de la variante 1
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-100" in html and "/ 100" in html

    second_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    assert second_url != session_url
    second = db_session.get(QuestionnaireSession, int(second_url.rsplit("/", 1)[-1]))
    assert _session_keys(second) == list(VARIANT_KEYS[1])
    assert second.parameters_json[EXAM_VARIANT_KEY] == 2

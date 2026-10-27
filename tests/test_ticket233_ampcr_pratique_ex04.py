"""Ticket #233 — AMPCR pratique écrite, EX04 « Examen blanc écrit — réseau, configuration et dépannage ».

Couvre : données des dossiers **recontrôlées ici** indépendamment (module standard `ipaddress`,
graphe du plan pour les domaines et la panne de SW1, bits du premier octet des MAC, résultats
des pings, plan d'adressage du cabinet, étendues DHCP, relevés DNS/route/APIPA/panne Internet,
fiche Wi-Fi, conversion % → dBm et canal, débits derrière le répéteur, accès effectifs partage +
NTFS, imprimante) ; schémas (validité, accessibilité, aucun verdict, fichiers statiques
identiques au SVG produit) ; questions (10 × 10 points = 100, réponses libres, 3 dossiers,
matière du ticket, exigences de l'emplacement, réponses absentes des énoncés) ; sujet (version
candidat sans corrigé, lignes de réponse, barème global) ; banque, seed, navigation (pas
d'entraînement), session d'examen (corrigé masqué avant remise, schémas dans leurs questions,
note sur 100) ; EX01 à EX03 et les cours PR inchangés.
Aucun appel IA réel : `FakeAIProvider` partout."""

import ipaddress
import re

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_bank import (
    PRACTICAL_BANK_IMPORTERS,
    PRACTICAL_COURSES_BY_CODE,
    _document_layout,
    get_practical_context,
    import_practical_bank,
    is_practical_exam_code,
    item_content,
    question_usage,
)
from app.v1.ampcr_pratique_ex04_bank import (
    ALL_ITEMS,
    DOSSIER_A,
    DOSSIER_B,
    DOSSIER_C,
    DOSSIER_DOCUMENTS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    ITEM_COURSES,
    ITEM_PARTS,
    PRACTICE_ITEMS,
    validate_items,
)
from app.v1.ampcr_pratique_ex04_course import EX04_SLUG, EX04_TITLE, ex04_course_sections
from app.v1.ampcr_pratique_ex04_figures import (
    AG_LEASES,
    AG_POOL,
    AG_POOL_NEW,
    AP_DIRECT_MBPS,
    APIPA_IPCONFIG,
    CAB_ERRORS,
    CAB_FIXED,
    CAB_HOSTS,
    CAB_POOL,
    CAB_SWITCH_PORTS,
    CALC_FACTS,
    CALC_ROWS,
    CALC_SMALLEST_PREFIX,
    DHCP_LOG,
    DIRECT_A,
    DIRECT_B_BAD,
    DIRECT_CABLE,
    DIRECT_CABLE_WITHOUT_AUTO,
    DIRECT_PING_1,
    DIRECT_PING_2,
    DNS_NSLOOKUP_OLD,
    DNS_NSLOOKUP_SRV,
    DNS_PING_IP,
    DNS_PING_NAME,
    EX04_FIGURES,
    KIND_FACTS,
    LIN_AP_DEFECTS,
    LIN_BEST_CHANNEL,
    LIN_MATRIX,
    LIN_MATRIX_FIXED,
    LIN_NEIGHBORS,
    LIN_POOL,
    LIN_SCAN,
    LINUX_ROUTE,
    MAC_FACTS,
    MAC_ROWS,
    OUTAGE_PING_GW,
    OUTAGE_PING_WEB,
    OUTAGE_TRACERT,
    PC3_TO_PC6_DST_MAC,
    PLAN_BROADCASTS,
    PLAN_COLLISIONS,
    PLAN_LAN,
    PRINTER_FIXED_IP,
    PRINTER_NEW_IP,
    PRINTER_PING,
    PRINTER_PORT_IP,
    R1_LAN_A,
    REP_MID_CLIENT,
    REP_MID_MBPS,
    REP_MID_UPLINK,
    REP_NOW_CLIENT,
    REP_NOW_MBPS,
    REP_NOW_UPLINK,
    SCREEN_WIDTH,
    SCREENS,
    SECR_COMPTA_LIMIT,
    SECR_COMPTA_LOCAL,
    SHARE_NET_USE,
    SHARE_PING,
    SHARE_PORT,
    STATIC_FIGURES,
    static_svg,
)
from app.v1.ampcr_pratique_pr21_figures import CABLE_ANY, CABLE_CROSS
from app.v1.ampcr_pratique_visuals import render_figure, validate_figure
from app.v1.assets import STATIC_DIR
from app.v1.models import Question, QuestionnaireSession, SessionMode, User
from app.v1.question_engine import validate_content
from app.v1.session_service import _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-ex04"
MODULE_COURSES = {"PR18", "PR19", "PR20", "PR21", "PR22", "PR23", "PR24", "PR25"}


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _subject_raw() -> str:
    return " ".join(c for _t, c in ex04_course_sections())


def _item(key: str):
    return next(i for i in EXAM_ITEMS if i.key == key)


def _expected(key: str) -> str:
    item = _item(key)
    return " ".join(c.expected for c in item.criteria) + " " + " ".join(item.correction)


def _stated(item) -> str:
    return " ".join((item.title, item.context, *item.instructions, *(d.content_text for d in item.documents)))


def _items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in EXAM_ITEMS
    ).lower()


def _ex04(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "EX04")
    return module, uaa


# =============================================================================================
# 1. Données des dossiers, recontrôlées indépendamment
# =============================================================================================


def _components(nodes: set[str], links: list[tuple[str, str]]) -> list[set[str]]:
    groups: list[set[str]] = []
    for node in sorted(nodes):
        if any(node in g for g in groups):
            continue
        group, todo = {node}, [node]
        while todo:
            current = todo.pop()
            for a, b in links:
                for x, y in ((a, b), (b, a)):
                    if x == current and y in nodes and y not in group:
                        group.add(y)
                        todo.append(y)
        groups.append(group)
    return groups


def test_plan_domains_and_sw1_failure():
    kinds = PLAN_LAN.kinds
    # Collision : chaque liaison est un domaine, sauf celles du hub qui n'en font qu'un.
    hub_links = [link for link in PLAN_LAN.links if "HUB" in link]
    assert PLAN_COLLISIONS == len(PLAN_LAN.links) - len(hub_links) + 1 == 7
    assert PLAN_BROADCASTS == sum(1 for link in PLAN_LAN.links if "R1" in link) == 2
    # Panne de SW1 : on retire SW1 et ses liaisons.
    nodes = set(kinds) - {"SW1"}
    groups = _components(nodes, [link for link in PLAN_LAN.links if "SW1" not in link])
    pcs = [sorted(n for n in g if kinds[n] == "pc") for g in groups]
    assert sorted(p for p in pcs if p) == [["PC1"], ["PC2"], ["PC3", "PC4", "PC5"], ["PC6", "PC7"]]
    expected = _expected("X01")
    assert "PC1 et PC2" in expected and "PC3, PC4 et PC5" in expected and "PC6 et PC7" in expected


def test_frames_and_netbeui():
    lan_a = ipaddress.ip_network("192.168.1.0/24")
    assert ipaddress.ip_address("192.168.2.16") not in lan_a and ipaddress.ip_address("192.168.1.14") in lan_a
    assert PC3_TO_PC6_DST_MAC == R1_LAN_A[2] == "00-1D-AA-4E-01-01"
    expected = _expected("X01")
    assert "00-1D-AA-4E-01-01" in expected and "3C-52-82-1A-01-14" in expected
    assert "non routable" in expected


def test_ipv4_calculations_with_ipaddress():
    for ref, ip, given in CALC_ROWS:
        net = ipaddress.ip_interface(f"{ip}/{given.lstrip('/')}").network
        facts = CALC_FACTS[ref]
        assert (facts.network, facts.broadcast, facts.prefix) == (
            str(net.network_address), str(net.broadcast_address), net.prefixlen)
        assert facts.usable == net.num_addresses - 2
        assert facts.first_host == str(net.network_address + 1) and facts.last_host == str(net.broadcast_address - 1)
    assert [CALC_FACTS[r].usable for r in "abcd"] == [62, 2046, 62, 30]
    assert ipaddress.ip_network("192.168.40.200/26", strict=False) != ipaddress.ip_network("192.168.40.77/26", strict=False)
    assert CALC_SMALLEST_PREFIX == 26 and 2 ** (32 - 27) - 2 < 50 <= 2 ** (32 - 26) - 2
    expected = _expected("X02")
    assert "10.12.207.255" in expected and "2 046" in expected and "172.20.5.191" in expected
    assert "192.168.40.192/26" in expected


def test_mac_bits_and_address_kinds():
    for ref, mac in MAC_ROWS:
        first = int(mac[:2], 16)
        assert MAC_FACTS[ref] == (bool(first & 1), bool(first & 2))
    assert MAC_FACTS == {"M1": (False, False), "M2": (False, True), "M3": (True, False)}
    assert ipaddress.ip_address("172.31.4.9") in ipaddress.ip_network("172.16.0.0/12")
    assert ipaddress.ip_address("172.32.4.9") not in ipaddress.ip_network("172.16.0.0/12")
    assert list(KIND_FACTS) == ["K1", "K2", "K3", "K4"]


def test_direct_connection_cable_and_pings():
    assert DIRECT_CABLE == CABLE_ANY and DIRECT_CABLE_WITHOUT_AUTO == CABLE_CROSS
    assert ipaddress.ip_interface(f"{DIRECT_A.ip}/24").network != ipaddress.ip_interface(f"{DIRECT_B_BAD.ip}/24").network
    assert DIRECT_B_BAD.gateway is None
    assert all("Défaillance générale" in line for line in DIRECT_PING_1[1:5])
    assert DIRECT_PING_2.count("Délai d'attente de la demande dépassé.") == 4
    assert "pare-feu" in _expected("X03") and "\\\\192.168.10.1\\Agenda" in _expected("X03")


def test_cabinet_plan_errors_and_fix():
    net = ipaddress.ip_network("192.168.10.0/24")
    low, high = (ipaddress.ip_address(a) for a in CAB_POOL)
    by_name = {h.name: h for h in CAB_HOSTS}
    assert by_name["PC-KINE1"].gateway != "192.168.10.254"
    assert by_name["PC-KINE2"].prefix == 16
    assert low <= ipaddress.ip_address(by_name["PC-KINE3"].ip) <= high and not by_name["PC-KINE3"].dhcp
    assert by_name["IMP-01"].ip == by_name["PC-KINE1"].ip
    assert len(CAB_ERRORS) == 4
    ips = [h.ip for h in CAB_FIXED]
    assert len(set(ips)) == len(ips)
    for host in CAB_FIXED[1:]:
        assert ipaddress.ip_address(host.ip) in net and host.prefix == 24 and host.gateway == "192.168.10.254"
        assert host.dhcp or not (low <= ipaddress.ip_address(host.ip) <= high)
    assert len(CAB_HOSTS) == 7 <= CAB_SWITCH_PORTS == 8  # 6 appareils + la liaison vers la box


def test_dns_case_ip_ok_name_ko():
    assert any(line.startswith("Réponse de 198.51.100.20") for line in DNS_PING_IP)
    assert "n'a pas pu trouver l'hôte" in " ".join(DNS_PING_NAME)
    assert "DNS request timed out." in DNS_NSLOOKUP_OLD and "Address:  192.168.50.53" in DNS_NSLOOKUP_OLD
    assert "Address:  198.51.100.20" in DNS_NSLOOKUP_SRV
    ipconfig = " ".join(SCREENS["dns_ipconfig"])
    assert "192.168.50.53" in ipconfig and "192.168.50.1" in ipconfig
    expected = _expected("X05")
    assert "connectivité IP intacte" in expected.replace("Connectivité", "connectivité") and "192.168.50.5" in expected


def test_route_and_dhcp_cases():
    assert not any(line.startswith("default") for line in LINUX_ROUTE)
    assert "ping: connect: Network is unreachable" in SCREENS["linux"]
    size = int(ipaddress.ip_address(AG_POOL[1])) - int(ipaddress.ip_address(AG_POOL[0])) + 1
    assert size == 20 == AG_LEASES
    assert ipaddress.ip_address("169.254.83.17") in ipaddress.ip_network("169.254.0.0/16")
    assert "169.254.83.17" in " ".join(APIPA_IPCONFIG) and "no address" in " ".join(DHCP_LOG)
    new = int(ipaddress.ip_address(AG_POOL_NEW[1])) - int(ipaddress.ip_address(AG_POOL_NEW[0])) + 1
    assert new == 100 and not any(
        int(ipaddress.ip_address(AG_POOL_NEW[0])) <= int(ipaddress.ip_address(f"192.168.50.{n}")) for n in (1, 5, 10, 21, 40))
    assert "default via 192.168.50.1 dev enp3s0" in _expected("X06")


def test_internet_outage_is_beyond_the_box():
    assert "  perdus = 0 (perte 0%)," in OUTAGE_PING_GW and "  perdus = 4 (perte 100%)," in OUTAGE_PING_WEB
    hops = [line for line in OUTAGE_TRACERT if re.match(r"\s+\d+ ", line)]
    assert "192.168.50.1" in hops[0] and all("Délai dépassé" in h for h in hops[1:])
    assert "pas le DNS" in _expected("X07") and "Rubriques" in _expected("X07")


def test_wifi_sheet_channel_and_repeater():
    params = {p for p, _fix in LIN_AP_DEFECTS}
    assert params == {"Sécurité", "Clé", "WPS", "Administration", "Micrologiciel", "Canal 2,4 GHz",
                      "Largeur 2,4 GHz", "SSID masqué", "Invités"}
    # Le relevé affiche des pourcentages : % = 2 × (dBm + 100), donc dBm = % / 2 − 100.
    pct = [int(line.split(":")[1].strip(" %")) for line in LIN_SCAN if "Signal" in line]
    dbms = [p / 2 - 100 for p in pct]
    assert dbms == [n.dbm for n in LIN_NEIGHBORS]
    strong = [(n.channel, n.dbm) for n in LIN_NEIGHBORS if n.dbm >= -80]

    def hits(ch: int) -> int:
        return sum(1 for c, _d in strong if abs(c - ch) < 5)

    assert {ch: hits(ch) for ch in (1, 6, 11)} == {1: 2, 6: 2, 11: 0} and LIN_BEST_CHANNEL == 11

    def rate(dbm: int) -> int:
        return 144 if dbm >= -60 else 104 if dbm >= -67 else 52 if dbm >= -75 else 13 if dbm >= -82 else 0

    assert REP_NOW_MBPS == min(rate(REP_NOW_UPLINK), rate(REP_NOW_CLIENT)) / 2 / 2 == 13
    assert AP_DIRECT_MBPS == 26 > REP_NOW_MBPS
    assert REP_MID_MBPS == min(rate(REP_MID_UPLINK), rate(REP_MID_CLIENT)) / 2 / 2 == 36
    assert REP_NOW_UPLINK < -67 <= REP_MID_UPLINK
    expected = _expected("X08")
    assert "13 Mb/s" in expected and "26 Mb/s" in expected and "36 Mb/s" in expected and "canal 11" in expected


def test_effective_access_matrix():
    # Recalcul à la main : par le réseau, le plus restrictif du partage et de NTFS.
    assert LIN_MATRIX == {
        "tlambert": {"Projets": "Modification", "Projets\\Concours": "Aucun accès", "Compta": "Aucun accès"},
        "nhaddad": {"Projets": "Lecture", "Projets\\Concours": "Aucun accès", "Compta": "Lecture"},
        "evermeer": {"Projets": "Modification", "Projets\\Concours": "Modification", "Compta": "Lecture"},
    }
    assert LIN_MATRIX_FIXED["nhaddad"]["Compta"] == "Modification"
    assert {k: v for k, v in LIN_MATRIX_FIXED.items() if k != "nhaddad"} == {
        k: v for k, v in LIN_MATRIX.items() if k != "nhaddad"}
    assert SECR_COMPTA_LIMIT == "le partage" and SECR_COMPTA_LOCAL == "Modification"


def test_printer_and_share_access():
    pool = (ipaddress.ip_address(LIN_POOL[0]), ipaddress.ip_address(LIN_POOL[1]))
    for ip in (PRINTER_PORT_IP, PRINTER_NEW_IP):
        assert pool[0] <= ipaddress.ip_address(ip) <= pool[1]
    assert not pool[0] <= ipaddress.ip_address(PRINTER_FIXED_IP) <= pool[1]
    assert "Impossible de joindre" in " ".join(PRINTER_PING)
    assert "Erreur système 53." in SHARE_NET_USE and "TcpTestSucceeded : False" in SHARE_PORT
    assert any("Réponse de 192.168.30.10" in line for line in SHARE_PING)
    assert "pas une question de droits" in _expected("X10")


def test_screens_fit_the_width():
    for name, lines in SCREENS.items():
        assert all(len(line) <= SCREEN_WIDTH for line in lines), name
    for item in EXAM_ITEMS:
        for document in item.documents:
            if document.kind == "console":
                assert all(len(line) <= SCREEN_WIDTH for line in document.content_text.splitlines()), document.title


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_without_verdict():
    assert len({f.key for f in EX04_FIGURES}) == len(EX04_FIGURES) == 3
    for figure in EX04_FIGURES:
        assert validate_figure(figure) == []
        html = str(render_figure(figure))
        assert 'role="img"' in html and "schéma non officiel" in html
        assert "✓" not in figure.svg and "✗" not in figure.svg
    plan_fig, cabinet, wifi = EX04_FIGURES
    assert "data-collision=\"\"" in plan_fig.svg and "Diffusion" not in plan_fig.svg and "domaines" not in plan_fig.svg
    assert "erreur" not in cabinet.svg.lower() and "Dupliqué" not in cabinet.svg and "192.168.10.150" in cabinet.svg
    for word in ("faible", "insuffisant", "excellent", "bon"):
        assert word not in wifi.svg
    assert f"{REP_NOW_UPLINK} dBm" in wifi.svg


def test_static_figure_files_are_the_generated_svg():
    assert len(STATIC_FIGURES) == 3
    for figure, path in STATIC_FIGURES:
        content = (STATIC_DIR / path).read_text()
        assert content == static_svg(figure)
        assert content.startswith("<svg ") and "xmlns=" in content and "<title>" in content


def test_schema_documents_point_to_static_files():
    images = {d.image for i in EXAM_ITEMS for d in i.documents if d.image}
    assert images == {path for _f, path in STATIC_FIGURES}
    layout = _document_layout(next(d for d in _item("X04").documents if d.image))
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/ex04-cabinet-mini-reseau.svg"
    assert "192.168.10.150" in layout["alt"] and "non officiel" in layout["notice"]


# =============================================================================================
# 3. Questions
# =============================================================================================


def test_items_valid_and_scored_on_100():
    assert validate_items() == []
    assert len(EXAM_ITEMS) == 10 and ALL_ITEMS == EXAM_ITEMS and PRACTICE_ITEMS == ()
    assert all(i.usage == "exam" and i.total_points == 10 for i in EXAM_ITEMS)
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 100
    assert all(i.question_type in ("long_answer", "document_analysis") for i in EXAM_ITEMS)
    assert [i.key for i in EXAM_ITEMS] == [f"X{n:02d}" for n in range(1, 11)]
    for item in EXAM_ITEMS:
        assert len(item.criteria) >= 3 and len(item.correction) >= 3
        assert set(ITEM_COURSES[item.key]) <= MODULE_COURSES
    assert {c for codes in ITEM_COURSES.values() for c in codes} == MODULE_COURSES


def test_three_dossiers_with_documents():
    for dossier in (DOSSIER_A, DOSSIER_B, DOSSIER_C):
        assert len(DOSSIER_DOCUMENTS[dossier]) >= 3
        items = [i for i in EXAM_ITEMS if ITEM_PARTS[i.key] == dossier]
        assert len(items) >= 2 and all(i.documents for i in items)
        used = {d.title for i in items for d in i.documents}
        assert used == {d.title for d in DOSSIER_DOCUMENTS[dossier]}  # chaque document sert


def test_ticket_subjects_are_all_evaluated():
    text = _items_text()
    for needle in (
        "osi", "tcp/ip", "topologie", "hub", "switch", "routeur", "netbeui", "masque", "diffusion", "/26",
        "adresse mac", "passerelle", "dhcp", "dns", "un seul câble",
        "auto mdi-x", "mini-réseau", "wi-fi", "wpa3", "répéteur", "partage", "ntfs", "imprimante", "ipconfig",
        "ip route", "nslookup", "ping", "tracert", "rapport",
    ):
        assert needle in text, needle
    # Ne pas confondre connectivité IP et résolution DNS : la question 5 le demande explicitement.
    assert "connectivité IP" in " ".join(_item("X05").instructions)


def test_items_cover_the_slot_requirements():
    slot = plan.EXERCISE_SLOTS_BY_CODE["EX04"]
    assert slot.ticket == 233 and slot.title == EX04_TITLE == PRACTICAL_COURSES_BY_CODE["EX04"].title
    covered = {r for i in EXAM_ITEMS for r in i.requirement_ids}
    assert set(slot.requirement_ids) <= covered
    assert covered <= set(plan.REQUIREMENTS_BY_ID)
    # Module 4 du plan = PR18 → PR25.
    assert {c.code for c in plan.COURSE_SLOTS if c.module_key == slot.module_key} == MODULE_COURSES


def test_answers_are_not_given_in_the_statements():
    for item in EXAM_ITEMS:
        prompt = item.prompt.lower()
        assert "que signifie" not in prompt and "développe" not in prompt
        assert "officiel" not in item.title.lower()
    for value in ("192.168.40.64", "10.12.207.255", "172.20.5.191", "192.168.40.223"):
        assert value not in _stated(_item("X02"))
    assert "Aucun accès" not in _stated(_item("X09")) and "pare-feu" not in _stated(_item("X03"))
    assert "≈ 13" not in _stated(_item("X08")) and "canal 11" not in _stated(_item("X08")).lower()
    assert "192.168.10.13" not in _stated(_item("X04")) and "pas le DNS" not in _stated(_item("X07"))


def test_items_content_matches_existing_question_types():
    for item in EXAM_ITEMS:
        ids = list(range(1, len(item.documents) + 1))
        content = item_content(item, ids)
        validate_content(item.question_type, 1, content)
        assert "Barème" in content["rubric"] and content["max_score"] == 10


# =============================================================================================
# 4. Sujet (version candidat)
# =============================================================================================


def test_subject_has_questions_without_corrections():
    raw = _subject_raw()
    for number, item in enumerate(EXAM_ITEMS, start=1):
        assert f"Question {number} — " in raw
        for step in item.correction:
            assert step[:60] not in raw
        for criterion in item.criteria:
            assert criterion.expected[:60] not in raw
    assert raw.count('class="jc-ex-answer"') == 10 and raw.count('class="jc-ex-dossier"') == 3
    assert "Corrigé de référence" not in raw and "<details" not in raw


def test_subject_presents_scoring_and_sources():
    text = _text(_subject_raw()).replace("**", "")
    assert "10 questions à réponse rédigée" in text and "sur 100" in text
    assert "pas la durée officielle" in text and "fictives" in text
    assert "/uaa/ampcr-pratique-ex04/exam" in text and "Ctrl + P" in text
    for code in plan.EXERCISE_SLOTS_BY_CODE["EX04"].requirement_ids:
        assert code in text
    for code in MODULE_COURSES:
        assert f"/uaa/ampcr-pratique-{code.lower()}" in text


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(title) for title, _c in ex04_course_sections()]
    assert kinds == ["theory", "theory", "theory", "theory", "theory", "method", "info"]


# =============================================================================================
# 5. Banque, seed, pages, sessions
# =============================================================================================


def test_seed_publishes_ex04_after_pr25_idempotently(db_session):
    module, uaa = _ex04(db_session)
    assert uaa.slug == SLUG == EX04_SLUG and uaa.is_published and uaa.title == EX04_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="EX04").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(ex04_course_sections())
    from app.v1.parcours import listed_uaas

    codes = [u.code for u in listed_uaas(db_session.get(Module, module.id))]
    assert codes.index("EX04") == codes.index("PR25") + 1
    assert codes.index("EX03") == codes.index("PR17") + 1 and codes.index("EX02") == codes.index("PR12") + 1
    assert codes.index("EX01") == codes.index("PR06") + 1
    assert {"EX01", "EX02", "EX03", "EX04"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_exam_reserve_only(db_session):
    module, uaa = _ex04(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert is_practical_exam_code("EX04") and not is_practical_exam_code("PR25")
    assert import_practical_bank(db_session, module, uaa) == 10
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert [question_usage(q) for q in questions] == ["exam"] * 10


def test_correction_context_is_ex04_specific():
    context = _pedagogical_context_for("EX04")
    assert context is get_practical_context("EX04") and context.course_key == SLUG
    assert context is not get_practical_context("EX03")
    notions = " ".join(context.allowed_notions)
    assert "NetBEUI" in notions and "APIPA" in notions and "NTFS" in notions and "WPA3" in notions
    assert "/100" in context.level and "mot-clé" in context.constraints and "DNS" in context.constraints


def test_subject_page_navigation_and_home(client, db_session):
    _ex04(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    assert "Sujet" in html and f'href="/uaa/{SLUG}/practice"' not in html and f"/uaa/{SLUG}/exam" in html
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in EX04_FIGURES}
    assert html.count('class="jc-ex-question"') == 10
    assert "examen blanc EX04" in html
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus\s+· \d examens blancs sur 6", home)  # EX05 (#201) publié ensuite
    assert client.get("/ampcr-pratique/matrice").status_code == 200
    pr25 = client.get("/uaa/ampcr-pratique-pr25").text
    assert 'href="/uaa/ampcr-pratique-pr25/practice"' in pr25


def test_practice_redirects_to_exam(authenticated_client, db_session):
    _ex04(db_session)
    response = authenticated_client.get(f"/uaa/{SLUG}/practice", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == f"/uaa/{SLUG}/exam"
    assert db_session.query(QuestionnaireSession).count() == 0


def test_exam_session_hides_corrections_and_scores_on_100(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _ex04(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="EX04", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert session.question_count == 10 and fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"EX04"}
    shown = set()
    for position in range(1, 11):
        page = authenticated_client.get(f"{session_url}?q={position}").text
        assert "Corrigé de référence" not in page and "Barème" not in page
        shown |= {path for _f, path in STATIC_FIGURES if path in page}
    assert shown == {path for _f, path in STATIC_FIGURES}  # les trois schémas dans leurs questions
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-100" in html and "/ 100" in html and "data-score-on-20" in html

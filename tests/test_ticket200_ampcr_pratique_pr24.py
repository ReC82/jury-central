"""Ticket #200 — AMPCR pratique écrite, PR24 « Dépannage réseau et Internet — dossiers
d'intervention écrits ».

Couvre : réseau de référence cohérent (plan sans erreur, étendue, équipements fixes hors étendue,
ports du switch) ; relevés fictifs **relus ici** (statistiques de ping, premier saut de tracert =
passerelle, réponses DNS, journaux DHCP, état Wi-Fi, ARP, routes, interface Linux) et largeur
mobile des captures ; calculs d'adressage des cas et exercices recalculés indépendamment ;
schémas SVG (réseau, ports, couches, arbres, documents, accessibilité) ; réponses auto-corrigées ;
contenu du cours (matière 1-15, 6 cas résolus, tableaux symptôme → action, 20 exercices,
mini-examen) ; banque, seed, pages et sessions. Aucun appel IA réel : `FakeAIProvider` partout."""

import ipaddress
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
from app.v1.ampcr_pratique_pr20_figures import AddressPlan, host_errors, plan_errors
from app.v1.ampcr_pratique_pr24_bank import (
    E01_HOST,
    E01_IN_GUEST,
    E01_IN_LAN,
    E04_LEASES,
    E04_POOL_SIZE,
    E08_LINES,
    E09_SHOWN,
    E10_CATEGORIES,
    E10_CORRECT,
    E14_ERRORS,
    E14_HOSTS,
    E16_LINES,
    E17_AFFECTED,
    EXAM_ITEMS,
    KIND_LOGS,
    KIND_MULTI,
    KIND_REPORT,
    KIND_TREE,
    PRACTICE_ITEMS,
    X04_FACTS,
    X04_REACHABLE,
    validate_items,
)
from app.v1.ampcr_pratique_pr24_course import (
    CASE3_HOST,
    PR24_TITLE,
    SYMPTOM_TABLE,
    pr24_course_sections,
)
from app.v1.ampcr_pratique_pr24_figures import (
    APIPA_HOST,
    DHCP_LOG_LINES,
    DOCUMENT_FIGURES,
    LAN_BY_NAME,
    LAN_HOSTS,
    LAN_NETWORK,
    LAYER_STEPS,
    NS_NXDOMAIN,
    NS_OK,
    NS_TIMEOUT,
    PING_LAN_OK_WAN_KO,
    POOL,
    PR24_FIGURES,
    ROUTER_IP,
    SCREEN_WIDTH,
    SERVER_IP,
    SWITCH_PORTS,
    TRACERT_STOPS,
    TREE_FIGURES,
    WAN_IP,
    WEB_IP,
    all_capture_lines,
    dig_lines,
    in_pool,
    is_documentation,
    nslookup_lines,
    ping_stats,
    pool_size,
    tracert_lines,
    win_ping_lines,
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

SLUG = "ampcr-pratique-pr24"


# --- Calcul IPv4 indépendant (arithmétique entière, sans `ipaddress`) ---------------------------


def _to_int(address: str) -> int:
    a, b, c, d = (int(x) for x in address.split("."))
    return (a << 24) | (b << 16) | (c << 8) | d


def _same_net(a: str, b: str, prefix: int) -> bool:
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    return _to_int(a) & mask == _to_int(b) & mask


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_text() -> str:
    return _text(" ".join(c for _t, c in pr24_course_sections())).lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _pr24(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR24")
    return module, uaa


# =============================================================================================
# 1. Réseau de référence et relevés
# =============================================================================================


def test_reference_network_is_consistent():
    hosts = tuple(h for h in LAN_HOSTS)
    assert plan_errors(AddressPlan(LAN_NETWORK, hosts, ROUTER_IP, SERVER_IP, POOL)) == []
    assert pool_size() == 100 == _to_int(POOL[1]) - _to_int(POOL[0]) + 1
    for host in LAN_HOSTS:
        assert host.dhcp == in_pool(host.ip), host.name  # fixes hors étendue, DHCP dedans
        assert _same_net(host.ip, ROUTER_IP, 24)
    assert is_documentation(WAN_IP) and is_documentation(WEB_IP)
    ports = {p.device for p in SWITCH_PORTS}
    assert {"BOX-01", "SRV-01", "NAS-01", "IMP-01", "AP-01"} <= ports
    assert [p.number for p in SWITCH_PORTS] == list(range(1, 11))
    assert next(p for p in SWITCH_PORTS if p.device == "AP-01").poe_w <= 12.95  # budget PoE 802.3af


def test_ping_outputs_have_computed_statistics():
    lines = win_ping_lines(ROUTER_IP, (0, None, 3, None))
    assert ping_stats(lines) == (4, 2, 2)
    assert "  perdus = 2 (perte 50%)," in lines
    assert ping_stats(PING_LAN_OK_WAN_KO[: len(PING_LAN_OK_WAN_KO) // 2]) == (4, 4, 0)
    assert "  perdus = 4 (perte 100%)," in PING_LAN_OK_WAN_KO
    assert ping_stats(E08_LINES[:10]) == (4, 2, 2)
    assert ping_stats(E16_LINES[:10]) == (4, 3, 1)


def test_tracert_first_hop_is_gateway_and_stops():
    assert TRACERT_STOPS[4].strip().endswith(ROUTER_IP)
    assert all("Délai dépassé." in line for line in TRACERT_STOPS[5:])
    complete = tracert_lines(WEB_IP, (ROUTER_IP, None, WEB_IP))
    assert complete[-1].endswith(WEB_IP) and "*" in complete[-2]


def test_dns_outputs_follow_status():
    ok = nslookup_lines("www.exemple.be", SERVER_IP, NS_OK, WEB_IP)
    assert ok[-1] == f"Address:  {WEB_IP}" and "Réponse ne faisant pas autorité :" in ok
    assert "Non-existent domain" in nslookup_lines("x.atelier.lan", "198.51.100.53", NS_NXDOMAIN)[-1]
    assert "DNS request timed out." in nslookup_lines("x", "192.168.20.6", NS_TIMEOUT)
    assert "status: NXDOMAIN" in " ".join(dig_lines("x", SERVER_IP, NS_NXDOMAIN))
    assert dig_lines("x", SERVER_IP, NS_TIMEOUT)[-1] == ";; no servers could be reached"


def test_dhcp_log_and_apipa_capture():
    text = "\n".join(DHCP_LOG_LINES)
    apipa_mac = APIPA_HOST.mac.lower().replace("-", ":")
    assert text.count(f"DHCPDISCOVER(eth0) {apipa_mac} ignored") == 3
    pc01 = LAN_BY_NAME["PC-01"]
    assert f"DHCPACK(eth0) {pc01.ip}" in text
    assert ipaddress.IPv4Address(APIPA_HOST.ip) in ipaddress.IPv4Network("169.254.0.0/16")
    assert APIPA_HOST.mask == "255.255.0.0" and APIPA_HOST.gateway is None
    assert E04_LEASES == E04_POOL_SIZE == pool_size()


def test_every_capture_fits_a_mobile_screen():
    lines = list(all_capture_lines())
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        for doc in item.documents:
            if doc.kind == "console":
                lines += doc.content_text.splitlines()
    assert len(lines) > 150
    too_long = [line for line in lines if len(line) > SCREEN_WIDTH]
    assert too_long == []


def test_every_ipv4_written_anywhere_is_valid_and_public_ones_are_documentation():
    everything = " ".join(c for _t, c in pr24_course_sections()) + _all_items_text()
    found = re.findall(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])", everything)
    assert len(found) > 200
    for address in set(found):
        ip = ipaddress.IPv4Address(address)  # lève si un octet dépasse 255
        if ip.is_global:
            assert is_documentation(address), address


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    assert len(PR24_FIGURES) >= 12 and len(DOCUMENT_FIGURES) >= 6 and len(TREE_FIGURES) == 3
    keys = [f.key for f in PR24_FIGURES]
    assert len(set(keys)) == len(keys)
    for figure in PR24_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "<title" in html and "<desc" in html and "schéma non officiel" in html
        assert 'viewBox="0 0 380' in figure.svg
    for figure in DOCUMENT_FIGURES:
        assert re.search(r"fictif|fictive", figure.caption.lower())


def test_lan_and_ports_figures_show_every_equipment():
    lan = next(f for f in PR24_FIGURES if f.key == "pr24-lan-reference")
    for host in LAN_HOSTS:
        assert host.name in lan.svg and host.ip in lan.svg and host.ip in lan.alt
    ports = next(f for f in PR24_FIGURES if f.key == "pr24-ports-switch")
    assert ports.svg.count("data-port=") == len(SWITCH_PORTS)
    assert 'data-port="10" data-state="pas de lien"' in ports.svg


def test_layer_procedure_and_trees():
    assert [name for name, _d in LAYER_STEPS] == [
        "Physique et liaison", "Adresse IP et masque", "Passerelle", "IP distante", "DNS", "Service ou application",
    ]
    master = TREE_FIGURES[0]
    assert master.svg.count("data-step=") == 6 and "NON" in master.svg and "OUI" in master.svg
    assert "radio" in TREE_FIGURES[1].caption and "authentification" in TREE_FIGURES[1].caption


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_LOGS) >= 8
    assert kinds.count(KIND_TREE) >= 5
    assert kinds.count(KIND_MULTI) >= 4
    assert kinds.count(KIND_REPORT) >= 3
    assert len(EXAM_ITEMS) == 10 and sum(i.total_points for i in EXAM_ITEMS) == 20
    assert {i.question_type for i in EXAM_ITEMS} <= {"short_answer", "long_answer", "document_analysis"}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(set(keys)) == len(keys)
    assert all({"AP-32", "AP-37"} <= set(i.requirement_ids) for i in PRACTICE_ITEMS + EXAM_ITEMS)
    assert sum(1 for i in EXAM_ITEMS if i.documents) >= 5


def test_auto_corrected_and_computed_answers():
    # E09 : la remise en ordre donne la procédure en couches ; affichage jamais dans l'ordre.
    e09 = next(i for i in PRACTICE_ITEMS if i.key == "E09")
    assert [e09.ordering.steps[i].split(" :")[0] for i in e09.ordering.correct] == [n for n, _d in LAYER_STEPS]
    assert list(E09_SHOWN) != list(range(len(LAYER_STEPS)))
    # E10 : couches attendues (écrites à la main).
    expected = ["DNS", "Physique", "Service", "Adressage", "Passerelle", "Physique", "Adressage", "Service"]
    assert [E10_CATEGORIES[i].split(" ")[0].rstrip(",").replace("Résolution", "DNS") for i in E10_CORRECT] == expected
    assert len(set(E10_CORRECT)) == 5  # toutes les couches sont utilisées
    # E01 : adresse du réseau invités.
    assert E01_IN_GUEST and not E01_IN_LAN and not _same_net(E01_HOST.ip, ROUTER_IP, 24)
    # E14 : chaque poste fautif est détecté, PC-A est correct.
    joined = " ".join(E14_ERRORS)
    assert "PC-A" not in joined and all(n in joined for n in ("PC-B", "PC-C", "PC-D"))
    assert in_pool(E14_HOSTS[3].ip) and E14_HOSTS[3].ip == LAN_BY_NAME["LT-01"].ip
    # E17 : postes servis par le second DHCP.
    assert E17_AFFECTED == ("PC-02", "PC-03")
    # X04 : /28, calcul indépendant ; aucun équipement local.
    assert (X04_FACTS.network, X04_FACTS.broadcast, X04_FACTS.usable) == ("192.168.20.32", "192.168.20.47", 14)
    assert not any(X04_REACHABLE.values())
    for ip in (ROUTER_IP, SERVER_IP, "192.168.20.10", "192.168.20.20", "192.168.20.30"):
        assert not _same_net("192.168.20.45", ip, 28)


def test_case3_mask_reasoning_is_computed():
    assert not _same_net(CASE3_HOST.ip, ROUTER_IP, CASE3_HOST.prefix)
    assert _same_net(CASE3_HOST.ip, LAN_BY_NAME["PC-01"].ip, CASE3_HOST.prefix)
    assert any("passerelle" in e for e in host_errors(CASE3_HOST))


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    assert "169.254.0.0/16" in text and "indice, pas une preuve" in text
    assert "pas une preuve" in text and "icmp" in text and "pare-feu" in text
    assert "le plus restrictif" in text and "445" in text
    assert "pas de lien = pas de diagnostic ip" in text
    for wrong in ("apipa prouve", "l'apipa prouve que le serveur", "internet est en panne car le nom",
                  "ping sans réponse prouve", "wpa3 est moins sûr", "5 ghz porte plus loin"):
        assert wrong not in text, wrong


def test_no_acronym_question_and_full_context():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.title, item.context, *item.instructions))
        assert not re.search(r"que signifie|que veut dire|développe[rz]? l'acronyme", text, re.IGNORECASE), item.key
        assert len(item.context) >= 150, item.key


def test_items_content_matches_existing_question_types():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        content = item_content(item, [1, 2][: len(item.documents)])
        validate_content(item.question_type, 1, content)


def test_six_resolved_cases_and_exam_not_in_course():
    text = _text(" ".join(c for _t, c in pr24_course_sections()))
    for case in ("Cas 1 — Un portable neuf en APIPA", "Cas 2 — Ping par adresse OK, nom interne KO",
                 "Cas 3 — Un masque incorrect", "Cas 4 — Wi-Fi connecté, sans Internet",
                 "Cas 5 — Réseau local OK, Internet KO", "Cas 6 — Imprimante réseau inaccessible malgré le ping"):
        assert case in text, case
    course = " ".join(content for _title, content in pr24_course_sections())
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


# =============================================================================================
# 4. Cours : toute la matière obligatoire (points 1 à 15 du ticket)
# =============================================================================================


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr24_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # 1 méthode en couches
        "symptôme exact", "périmètre", "un poste ou tous", "filaire ou wi-fi", "local ou internet", "chronologie",
        "changements récents", "topologie", "hypothèses", "tests non destructifs", "corrélation", "preuve",
        # 2 physique / liaison
        "fibre", "rj45", "voyants de lien", "port du switch", "vitesse", "duplex", "auto mdi-x", "erreurs crc",
        "blindage", "100 m", "poe", "802.3af", "signal", "interférences",
        # 3 configuration IP
        "masque", "cidr", "table de routage", "adresse mac", "même sous-réseau", "doublon", "apipa",
        "réservation",
        # 4 DHCP
        "dora", "discover", "offer", "request", "acknowledge", "bail", "étendue épuisée", "mauvais pool",
        "relais", "option 3", "option 6", "ipconfig /all", "ipconfig /release", "ipconfig /renew",
        # 5 DNS
        "résolution de noms", "nslookup", "dig", "nxdomain", "cache", "dns interne", "dns public",
        "ipconfig /flushdns",
        # 6 passerelle / routage
        "passerelle", "route par défaut", "routage inter-sous-réseaux", "nat", "acl", "filtrage icmp",
        # 7 switch / VLAN
        "table mac", "ports désactivés", "vlan", "trunk", "access", "sans indice",
        # 8 Wi-Fi
        "ssid", "bssid", "association", "authentification", "wpa2", "wpa3", "clé", "2,4 ghz", "5 ghz",
        "répéteur", "problème radio", "problème ip",
        # 9 partages
        "découverte du réseau", "chemin unc", "ntfs", "domaine", "groupe de travail", "pare-feu",
        "file d'impression", "spouleur",
        # 10 Windows
        "ping", "tracert", "arp -a", "route print", "netstat", "get-nettcpconnection", "test-netconnection",
        "lecture ou modification", "limites de ping",
        # 11 Linux
        "ip addr", "ip route", "ip neigh", "traceroute", "tracepath", "ss -tunap", "journalctl", "nmcli",
        "resolvectl", "ne pas présumer",
        # 12 procédure
        "état physique", "ip distante", "application ou service", "résultat attendu", "branche",
        # 13 pannes combinées
        "câble défectueux + dns", "mauvais masque + mauvaise passerelle", "dhcp intermittent",
        "réseau local ok mais internet ko", "internet ok mais partage ko", "wi-fi associé sans ip",
        "lenteur intermittente", "test discriminant",
        # 14 sécurité
        "réseau de production", "état initial", "retour arrière", "scan intrusif", "confidentialité des journaux",
        # 15 rapport
        "contexte", "schéma", "tests et sorties", "cause confirmée", "incertaine", "tests finaux", "prévention",
        "restitution",
        # encadrés et glossaire
        "à retenir", "piège fréquent", "méthode examen", "glossaire",
    ):
        assert notion in text, notion


def test_symptom_tables_have_every_column_and_multiple_causes():
    assert len(SYMPTOM_TABLE) >= 6
    assert sum(1 for _s, causes, *_r in SYMPTOM_TABLE if len(causes) >= 3) >= 2
    text = _course_text()
    for label in ("causes possibles :", "test discriminant :", "résultat :", "action :"):
        assert text.count(label) >= len(SYMPTOM_TABLE), label


def test_course_flags_requirements_complements_and_fictive_supports():
    raw = " ".join(c for _t, c in pr24_course_sections())
    text = _text(raw)
    for req in ("AP-32", "AP-37", "AP-C01", "AP-C03"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    for link in ("/uaa/ampcr-mc19", "/uaa/ampcr-mc20", "/uaa/ampcr-mc22", "/uaa/ampcr-mc24", "/uaa/ampcr-mc25",
                 "/uaa/ampcr-mc31", "/uaa/ampcr-mc33", "/uaa/ampcr-pratique-pr20", "/uaa/ampcr-pratique-pr15"):
        assert link in raw, link


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr24_course_sections()]
    assert kinds.count("exam") == 1 and kinds.count("exercise") == 1 and kinds.count("example") == 1
    assert kinds.count("info") == 1 and kinds[-1] == "info" and "summary" in kinds and "warning" in kinds
    assert kinds[1:12] == ["theory"] * 11


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_and_requirements():
    slot = plan.COURSE_SLOTS_BY_CODE["PR24"]
    assert slot.ticket == 200 and slot.title == PR24_TITLE == PRACTICAL_COURSES_BY_CODE["PR24"].title
    assert set(slot.requirement_ids) == {"AP-32", "AP-37"}
    assert "panne internet" in plan.REQUIREMENTS_BY_ID["AP-32"].text
    assert "accès au réseau" in plan.REQUIREMENTS_BY_ID["AP-37"].text


def test_seed_publishes_pr24_in_practical_module_idempotently(db_session):
    module, uaa = _pr24(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR24_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR24").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr24_course_sections())
    assert {"PR06", "PR11", "PR15", "PR16", "PR20", "PR24"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr24(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr24_specific():
    context = _pedagogical_context_for("PR24")
    assert context is get_practical_context("PR24")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    assert "APIPA 169.254.0.0/16" in notions and "NXDOMAIN" in notions and "port 445" in notions
    assert "l'APIPA prouve que le serveur DHCP est en panne" in context.constraints
    assert "mot-clé" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr24(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR24_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html


def test_practical_home_and_matrix_show_pr24(client, db_session):
    _pr24(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "6 cours publiés" in home
    for req in ("AP-32", "AP-37"):
        assert plan.requirement_status(req, {"PR24"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr24(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR24"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr24(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR24", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr24(db_session)
    for _ in range(2):  # 20 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

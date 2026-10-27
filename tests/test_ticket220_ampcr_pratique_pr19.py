"""Ticket #220 — AMPCR pratique écrite, PR19 « Topologies, OSI, TCP/IP, NetBEUI et équipements ».

Couvre : données de référence et calculs **recontrôlés ici** indépendamment (liaisons d'un
maillage, effet d'une panne selon la topologie, couches OSI et TCP/IP, tailles
d'encapsulation et bourrage, champs de la trame, ports, domaines de collision et de diffusion,
adresses des trames sur le chemin d'un paquet, couche en défaut, NetBEUI non routable) ;
schémas SVG (validité, accessibilité, données dessinées, schémas à compléter sans leurs
réponses, fichiers statiques) ; exercices et mini-examen (format du socle, classements et
remises en ordre auto-corrigés, nombres des corrigés, 6 schémas à compléter et 5 choix
d'équipement) ; cours (matière du ticket, 3 procédures, 5 cas résolus, liens, supports
fictifs, cartes) ; banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr19_bank import (
    E11,
    E13_AFTER,
    E13_BROADCASTS,
    E13_COLLISIONS,
    E16_AFTER,
    E16_BEFORE,
    E20_MESH,
    E20_STAR,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_DIAG,
    KIND_EQUIPMENT,
    KIND_LAYERS,
    KIND_ORDER,
    KIND_SCHEMA,
    KIND_TOPO,
    PRACTICE_ITEMS,
    REQ,
    X03,
    X04_LOCAL,
    X04_REMOTE,
    X05_BROADCASTS,
    X05_COLLISIONS,
    X10_MESH,
    validate_items,
)
from app.v1.ampcr_pratique_pr19_course import CASES, PR19_SLUG, PR19_TITLE, pr19_course_sections
from app.v1.ampcr_pratique_pr19_figures import (
    BOX_LAN,
    BOX_WAN,
    BUS_4,
    DIAG_STEPS,
    DOMAINS_BLANK_LAN,
    DOMAINS_LAN,
    DOUBLE_RING_5,
    ENCAP_EXAMPLE,
    ETH_MAX_FRAME,
    ETH_MIN_FRAME,
    FRAME_FIELDS,
    ISP_ROUTER,
    L1,
    L2,
    L3,
    L4,
    L7,
    MESH_4,
    N_HUB,
    N_PC,
    N_ROUTER,
    N_SWITCH,
    OSI_BLANK_ANSWERS,
    OSI_LAYERS,
    PATH_FRAMES,
    PATH_STEPS,
    PC,
    PC_PEER,
    PR19_FIGURES,
    PROCEDURES,
    PROTOCOL_LAYER,
    RING_5,
    SERVER_IP,
    STAR_5,
    STATIC_FIGURES,
    TOPO_BLANK_ORDER,
    TOPO_BUS,
    TOPO_MESH,
    TOPO_RING,
    TOPO_STAR,
    TREE,
    Lan,
    broadcast_domain_of_links,
    broadcast_domains,
    collision_domain_of_links,
    collision_domains,
    crosses_router,
    domains_svg,
    encapsulate,
    fault_layer,
    isolated_stations,
    lan_frame,
    mesh_links,
    next_hop,
    octets,
    service_for_port,
    static_svg,
    tcpip_layer_for,
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

SLUG = "ampcr-pratique-pr19"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr19_course_sections())


def _course_text() -> str:
    return _text(_course_raw()).replace("**", "").replace("`", "").lower()


def _all_items_text() -> str:
    return " ".join(
        " ".join((i.title, i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )


def _item(key: str):
    return next(i for i in PRACTICE_ITEMS + EXAM_ITEMS if i.key == key)


def _pr19(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR19")
    return module, uaa


# =============================================================================================
# 1. Données de référence et calculs, recontrôlés indépendamment
# =============================================================================================


def test_topology_links_and_failures():
    assert [mesh_links(n) for n in (2, 3, 4, 5, 6, 10)] == [1, 3, 6, 10, 15, 45]
    assert isolated_stations(STAR_5, link=("SW", "PC3")) == {"PC3"}
    assert isolated_stations(STAR_5, link=("PC3", "SW")) == {"PC3"}  # sens de la liaison indifférent
    assert isolated_stations(STAR_5, node="SW") == set(STAR_5.stations)
    assert isolated_stations(STAR_5, node="PC2") == frozenset()  # un poste éteint ne gêne personne
    assert isolated_stations(BUS_4, link=("PC2", "PC3")) == set(BUS_4.stations)
    assert isolated_stations(BUS_4, terminator=True) == set(BUS_4.stations)
    assert isolated_stations(BUS_4, node="PC4") == frozenset()  # T en place
    assert isolated_stations(RING_5, link=("PC1", "PC2")) == set(RING_5.stations)
    assert isolated_stations(DOUBLE_RING_5, link=("PC1", "PC2")) == frozenset()
    assert isolated_stations(MESH_4, link=("R1", "R2")) == frozenset()
    assert isolated_stations(TREE, node="SW2") == {"PC4", "PC5", "PC6"}
    assert isolated_stations(TREE, link=("SW0", "SW1")) == {"PC1", "PC2", "PC3"}
    assert isolated_stations(TREE, node="SW0") == set(TREE.stations)


def test_osi_tcpip_and_protocol_layers():
    assert [layer.number for layer in OSI_LAYERS] == [7, 6, 5, 4, 3, 2, 1]
    assert [layer.name for layer in OSI_LAYERS] == [
        "Application", "Présentation", "Session", "Transport", "Réseau", "Liaison de données", "Physique"]
    pdu = {layer.number: layer.pdu for layer in OSI_LAYERS}
    assert pdu[1] == "bit" and pdu[2] == "trame" and pdu[3] == "paquet" and pdu[4].startswith("segment")
    assert [tcpip_layer_for(n) for n in range(1, 8)] == [
        "Accès réseau", "Accès réseau", "Internet", "Transport", "Application", "Application", "Application"]
    assert PROTOCOL_LAYER["DNS"] == PROTOCOL_LAYER["DHCP"] == 7  # protocoles d'application, sur UDP
    assert PROTOCOL_LAYER["ICMP"] == PROTOCOL_LAYER["IP"] == 3 and PROTOCOL_LAYER["TCP"] == PROTOCOL_LAYER["UDP"] == 4
    assert PROTOCOL_LAYER["Ethernet"] == 2
    assert OSI_BLANK_ANSWERS == {"①": "Présentation", "②": "Transport", "③": "Réseau", "④": "Liaison de données",
                                 "⑤": "Internet", "⑥": "paquet", "⑦": "trame"}


def test_encapsulation_sizes_and_padding():
    e = ENCAP_EXAMPLE
    assert (e.data, e.segment, e.packet, e.padding, e.frame) == (1460, 1480, 1500, 0, 1518)
    assert (E11.segment, E11.packet, E11.padding, E11.frame) == (48, 68, 0, 86)
    assert (X03.segment, X03.packet, X03.padding, X03.frame) == (20, 40, 6, 64)
    assert encapsulate(6, "TCP").frame == 64 and encapsulate(6, "TCP").padding == 0  # 6 + 20 + 20 = 46
    assert encapsulate(26, "TCP").frame == 84 and encapsulate(5, "TCP").padding == 1
    assert encapsulate(18, "UDP").padding == 0 and encapsulate(17, "UDP").padding == 1
    with pytest.raises(ValueError):
        encapsulate(1461, "TCP")  # dépasse la MTU
    assert (ETH_MIN_FRAME, ETH_MAX_FRAME) == (64, 1518)
    assert [size for _n, size in FRAME_FIELDS] == ["6", "6", "2", "46 à 1 500", "4"]
    assert octets(1518) == "1 518" and octets(64) == "64"


def test_ports_and_netbeui():
    assert service_for_port(443) == "HTTPS" and service_for_port(53) == "DNS" and service_for_port(587) == "SMTP"
    assert service_for_port(445) == "SMB" and service_for_port(3389) == "RDP" and service_for_port(67) == "DHCP"
    with pytest.raises(KeyError):
        service_for_port(8)
    assert crosses_router("TCP/IP") and crosses_router("IPX/SPX") and not crosses_router("NetBEUI")


def test_collision_and_broadcast_domains():
    assert collision_domains(DOMAINS_LAN) == 7 and broadcast_domains(DOMAINS_LAN) == 2
    domains = collision_domain_of_links(DOMAINS_LAN)
    hub_links = [d for (a, b), d in zip(DOMAINS_LAN.links, domains, strict=True) if "HUB" in (a, b)]
    assert len(hub_links) == 3 and len(set(hub_links)) == 1
    assert len(set(broadcast_domain_of_links(DOMAINS_LAN))) == 2
    assert (E13_COLLISIONS, E13_BROADCASTS, E13_AFTER) == (6, 2, 9)
    assert (E16_BEFORE, E16_AFTER) == (1, 9)
    assert (X05_COLLISIONS, X05_BROADCASTS) == (14, 1)
    # Un switch seul : un domaine par liaison, un seul domaine de diffusion.
    lan = Lan((("S", N_SWITCH, 0, 0), ("A", N_PC, 0, 0), ("B", N_PC, 0, 0)), (("S", "A"), ("S", "B")))
    assert collision_domains(lan) == 2 and broadcast_domains(lan) == 1
    # Un hub seul : tout partagé.
    hub = Lan((("H", N_HUB, 0, 0), ("A", N_PC, 0, 0), ("B", N_PC, 0, 0)), (("H", "A"), ("H", "B")))
    assert collision_domains(hub) == 1 and broadcast_domains(hub) == 1
    # Routeur à trois interfaces vers trois postes : trois domaines de chaque.
    router = Lan((("R", N_ROUTER, 0, 0),) + tuple((n, N_PC, 0, 0) for n in "ABC"), tuple(("R", n) for n in "ABC"))
    assert collision_domains(router) == broadcast_domains(router) == 3


def test_packet_path_addresses():
    assert next_hop(PC.ip, 24, PC_PEER.ip, BOX_LAN.ip) == PC_PEER.ip
    assert next_hop(PC.ip, 24, SERVER_IP, BOX_LAN.ip) == BOX_LAN.ip
    first, second = PATH_FRAMES
    assert (first.src_mac, first.dst_mac, first.src_ip, first.dst_ip) == (PC.mac, BOX_LAN.mac, PC.ip, SERVER_IP)
    assert (second.src_mac, second.dst_mac, second.src_ip, second.dst_ip) == (BOX_WAN.mac, ISP_ROUTER.mac, BOX_WAN.ip, SERVER_IP)
    assert first.dst_ip == second.dst_ip and first.src_mac != second.src_mac
    assert X04_LOCAL.dst_mac == PC_PEER.mac and X04_REMOTE.dst_mac == BOX_LAN.mac
    assert lan_frame(PC, "192.168.1.200", arp={"192.168.1.200": "AA"}).dst_mac == "AA"
    for address in (BOX_WAN.ip, ISP_ROUTER.ip, SERVER_IP):  # adresses de documentation (RFC 5737)
        assert address.startswith(("203.0.113.", "198.51.100."))


def test_fault_layer_bottom_up():
    assert fault_layer(link_light=True) is None
    assert fault_layer(link_light=False, ip_ok=False, app_ok=False) == L1  # la plus basse d'abord
    assert fault_layer(link_light=True, right_vlan=False) == L2
    assert fault_layer(link_light=True, gateway_ping=False) == L3
    assert fault_layer(link_light=True, port_open=False, app_ok=False) == L4
    assert fault_layer(link_light=True, app_ok=False) == L7


def test_procedures_order():
    assert [t for t, _s in PROCEDURES] == [
        "Choisir l'équipement adapté", "Suivre un paquet du PC à Internet", "Diagnostiquer couche par couche"]
    path = [label for label, _d in PATH_STEPS]
    assert path.index("Comparer les réseaux") < path.index("Trouver la MAC") < path.index("Encapsuler") < path.index("Passer le routeur")
    assert [label for label, _d in DIAG_STEPS] == [
        "Physique (1)", "Liaison (2)", "Réseau (3)", "Transport (4)", "Application (7)", "Consigner"]


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    all_figures = PR19_FIGURES + tuple(f for f, _p in STATIC_FIGURES)
    keys = [f.key for f in all_figures]
    assert len(keys) == len(set(keys)) == 16 and len(PR19_FIGURES) >= 4  # ticket : ≥ 4 schémas
    for figure in all_figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR19_FIGURES}
    topo = by_key["pr19-topologies"].svg
    assert re.findall(r'data-topology="([^"]+)"', topo) == [TOPO_BUS, TOPO_STAR, TOPO_RING, TOPO_MESH]
    assert len(re.findall(r'data-link="star-\d"', topo)) == 5 and len(re.findall(r'data-link="ring-\d"', topo)) == 5
    assert len(re.findall(r'data-link="mesh-\d\d"', topo)) == mesh_links(4) and topo.count("data-terminator") == 2
    osi = by_key["pr19-osi-tcpip"].svg
    assert re.findall(r'data-layer="(\d)" data-name="([^"]+)"', osi) == [(str(layer.number), escape(layer.name)) for layer in OSI_LAYERS]
    assert re.findall(r'data-tcpip="([^"]+)"', osi) == ["Application", "Transport", "Internet", "Accès réseau"]
    frame = by_key["pr19-trame-ethernet"].svg
    assert re.findall(r'data-field="([^"]+)" data-size="([^"]+)"', frame) == [(escape(n), s) for n, s in FRAME_FIELDS]
    domains = by_key["pr19-domaines"].svg
    assert [int(c) for c in re.findall(r'data-collision="(\d+)"', domains)] == collision_domain_of_links(DOMAINS_LAN)
    assert sorted(re.findall(r'data-broadcast="(\d)"', domains)) == ["1", "2"]
    encap = by_key["pr19-encapsulation"].svg
    assert "Trame Ethernet : 1 518 octets" in encap and "Paquet IP : 1 500 octets" in encap
    path = by_key["pr19-chemin-paquet"].svg
    for frame_view in PATH_FRAMES:
        for value in (frame_view.src_mac, frame_view.dst_mac, frame_view.src_ip, frame_view.dst_ip):
            assert value in path
    for key, (_title, steps) in zip(("pr19-procedure-choix", "pr19-procedure-chemin", "pr19-procedure-diagnostic"),
                                    PROCEDURES, strict=True):
        for index, (label, _d) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in by_key[key].svg, (key, label)


def test_schemas_to_complete_hide_their_answers():
    by_key = {f.key: f.svg for f, _p in STATIC_FIGURES}
    topo = by_key["pr19-topologies-a-completer"]
    assert "data-topology" not in topo and "Maillage" not in topo and ">Bus<" not in topo and "Étoile" not in topo
    assert "Anneau" not in topo and [f"{n} ?" in topo for n in "①②③④"] == [True] * 4
    assert TOPO_BLANK_ORDER != (TOPO_BUS, TOPO_STAR, TOPO_RING, TOPO_MESH)  # ordre différent du cours
    osi = by_key["pr19-osi-a-completer"]
    for hidden in ("Présentation", "Réseau", "Liaison", "Internet", "paquet", "trame"):
        assert hidden not in osi, hidden
    assert ">4<" in osi and ">Application<" in osi
    encap = by_key["pr19-encapsulation-a-completer"]
    for answer in ("48 octets", "68 octets", "86 octets", "UDP 8"):
        assert answer not in encap, answer
    path = by_key["pr19-chemin-a-completer"].split("Champ")[1]  # tableau des trames
    first, second = PATH_FRAMES
    assert first.dst_mac not in path and second.src_mac not in path and second.dst_mac not in path
    assert second.src_ip not in path and path.count(SERVER_IP) == 1  # IP destination de la trame 1 seulement
    domains = by_key["pr19-domaines-a-completer"]
    assert 'data-collision=""' in domains and "data-broadcast" not in domains and "<circle" not in domains
    frame = by_key["pr19-trame-a-completer"]
    for hidden in ("destination", "source", "Type", "FCS"):
        assert hidden not in frame, hidden
    assert domains_svg(DOMAINS_BLANK_LAN) != by_key["pr19-domaines-a-completer"]


def test_static_figure_files_are_the_generated_svg():
    assert len(STATIC_FIGURES) == 6
    for figure, path in STATIC_FIGURES:
        content = (STATIC_DIR / path).read_text()
        assert content == static_svg(figure)
        assert content.startswith("<svg ") and "xmlns=" in content and "<title>" in content


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 18 and len(EXAM_ITEMS) == 10  # ticket : ≥ 18 exercices, mini-examen /20
    assert sum(i.total_points for i in EXAM_ITEMS) == EXAM_TOTAL_POINTS == 20
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_SCHEMA) == 6 and kinds.count(KIND_EQUIPMENT) >= 5
    for kind in (KIND_ORDER, KIND_TOPO, KIND_LAYERS, KIND_DIAG):
        assert kind in kinds
    schema_images = {d.image for i in PRACTICE_ITEMS for d in i.documents if d.image}
    assert schema_images == {p for _f, p in STATIC_FIGURES}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert covered == REQ == set(plan.COURSE_SLOTS_BY_CODE["PR19"].requirement_ids)
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 5


def test_auto_corrected_answers():
    def ordered(key: str) -> list[str]:
        item = _item(key)
        return [item.ordering.steps[i].split(" — ")[0] for i in item.ordering.correct]

    assert ordered("E01") == [label for label, _d in PATH_STEPS]
    assert ordered("E02") == [label for label, _d in DIAG_STEPS]
    assert ordered("E03") == ["Application", "Transport", "Réseau", "Liaison", "Physique"]

    def find(key: str, needle: str) -> str:
        c = _item(key).classification
        index = next(i for i, e in enumerate(c.elements) if needle in e)
        return c.categories[c.correct[index]]

    assert find("E04", "jeton") == TOPO_RING and find("E04", "T BNC") == TOPO_BUS and find("E04", "50 Ω") == TOPO_BUS
    assert find("E04", "propre câble") == TOPO_STAR and find("E04", "trois autres") == TOPO_MESH
    assert find("E05", "serveur DHCP") == "Service" and find("E05", "TCP :") == "Protocole" and find("E05", "switch 24") == "Équipement"
    assert find("E05", "partage") == "Service" and find("E05", "IP :") == "Protocole" and find("E05", "point d'accès") == "Équipement"
    assert find("E06", "DNS") == L7 and find("E06", "DHCP") == L7 and find("E06", "ICMP") == L3
    assert find("E06", "UDP") == L4 and find("E06", "Wi-Fi") == L2
    assert find("E07", "192.168.2.0") == "Routeur" and find("E07", "tous ses autres ports") == "Hub"
    assert find("E07", "VDSL") == "Modem" and find("E07", "par radio") == "Point d'accès" and find("E07", "Régénère") == "Répéteur"
    assert find("E07", "Apprend la MAC") == "Switch"
    assert find("E08", "nslookup") == L7 and find("E08", "écrasé") == L1 and find("E08", "VLAN") == L2
    assert find("E08", "passerelle par défaut vide") == L3 and find("E08", "3389") == L4 and find("E08", "fil 6") == L1
    assert find("E08", "identifiant") == L7
    for item in PRACTICE_ITEMS:
        if item.ordering is not None:
            assert list(item.ordering.correct) != list(range(len(item.ordering.steps))), item.key
        if item.classification is not None:
            correct = list(item.classification.correct)
            # ticket #150 : la première catégorie n'est jamais la réponse de tous les premiers éléments
            assert correct[: len(item.classification.categories)] != list(range(len(item.classification.categories))), item.key
            assert len(set(correct)) == len(item.classification.categories), item.key


def test_numbers_in_corrections_match_calculations():
    def text(key: str) -> str:
        item = _item(key)
        return " ".join((*item.correction, *(c.expected for c in item.criteria)))

    assert "86 octets" in text("E11") and "48" in text("E11") and "68" in text("E11")
    assert "6" in text("E13") and "9 au total" in text("E13")
    assert (E20_STAR, E20_MESH) == (4, 10) and "10 liaisons" in text("E20")
    assert "64 octets" in text("X03") and "6 octets de bourrage" in text("X03")
    assert "14" in text("X05") and X10_MESH == 15 and "15 liaisons" in text("X10")
    assert PC_PEER.mac in text("X04") and BOX_LAN.mac in text("X04")
    assert BOX_WAN.mac in text("E12") and ISP_ROUTER.mac in text("E12") and BOX_WAN.ip in text("E12")
    assert "587" in text("E19") and "445" in text("E19") and "3389" in text("E19")
    assert "non routable" in text("E18").lower() and "non routable" in text("X07").lower()


def test_schema_documents_point_to_static_files():
    item = _item("E13")
    layout = _document_layout(item.documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr19-domaines-a-completer.svg"
    assert "hub" in layout["alt"] and "non officiel" in layout["notice"]


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("bus", "étoile", "anneau", "maillage", "n × (n − 1) ÷ 2", "encapsulation", "fcs", "1 518",
                  "64", "arp", "non routable", "netbios", "routeur", "passerelle par défaut", "modem",
                  "point d'accès", "répéteur", "domaine de collision", "domaine de diffusion", "vlan", "nat",
                  "443", "53", "protocole", "service", "équipement"):
        assert right in text, right
    for wrong in ("netbeui est routable", "le switch sépare les domaines de diffusion", "le hub sépare",
                  "dns travaille à la couche 3", "le switch route", "mac du serveur d'internet dans la trame 1",
                  "l'adresse ip de destination change"):
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
    assert [title for title, *_r in CASES] == [
        "Cas 1 — Atelier en bus coaxial et logiciel NetBEUI", "Cas 2 — Équiper une PME de A à Z",
        "Cas 3 — Suivre un paquet jusqu'au site web", "Cas 4 — Un hub qui ralentit tout",
        "Cas 5 — L'intranet ne s'ouvre pas : diagnostic par couche"]
    for title, *_r in CASES:
        assert escape(title) in _course_raw() or title in text, title
    assert text.count("Conclusion rédigée.") == 5
    for i in (1, 2, 3):
        assert f"Procédure {i} —" in text, i
    course = _course_raw()
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key
    for figure, _path in STATIC_FIGURES:
        assert f'id="fig-{figure.key}"' in course, figure.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr19_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "bus", "étoile", "anneau", "maillage", "avantages", "défauts", "panne", "7 couches", "encapsulation",
        "tcp/ip", "ethernet", "802.3", "mac", "arp", "ip", "tcp", "udp", "adresses", "ports", "netbeui",
        "non routable", "hub", "pont", "switch", "routeur", "passerelle", "modem", "point d'accès", "répéteur",
        "collision", "diffusion", "vlan", "chemin d'un paquet", "internet", "diagnostic", "couche par couche",
        "protocole", "service", "équipement",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-23", "AP-29", "AP-31"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "rfc 5737" in text.lower()
    for link in ("/uaa/ampcr-mc13", "/uaa/ampcr-mc14", "/uaa/ampcr-mc21", "/uaa/ampcr-mc23",
                 "/uaa/ampcr-pratique-pr16", "/uaa/ampcr-pratique-pr18", "/uaa/ampcr-pratique-pr20",
                 "/uaa/ampcr-pratique-pr24", f"/uaa/{PR19_SLUG}/practice", f"/uaa/{PR19_SLUG}/exam"):
        assert link in raw, link
    for unpublished in ("/uaa/ampcr-pratique-pr21", "/uaa/ampcr-pratique-pr23", "/uaa/ampcr-pratique-pr25"):
        assert unpublished not in raw, unpublished
    anchors = set(re.findall(r'id="(pr19-e\d\d)"', raw))
    assert anchors == {f"pr19-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr19-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr19_course_sections()]
    assert kinds[:10] == ["theory"] * 10
    assert kinds[10:] == ["example", "warning", "exercise", "exam", "summary", "info"]


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR19"]
    assert slot.ticket == 220 and slot.title == PR19_TITLE == PRACTICAL_COURSES_BY_CODE["PR19"].title


# =============================================================================================
# 5. Seed, banque, correction
# =============================================================================================


def test_seed_publishes_pr19_in_practical_module_idempotently(db_session):
    module, uaa = _pr19(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR19_TITLE and uaa.position == 19
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR19").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr19_course_sections())
    assert {"PR18", "PR19", "PR20"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR18") < ordered.index("PR19") < ordered.index("PR20")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr19(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr19_specific():
    context = _pedagogical_context_for("PR19")
    assert context is get_practical_context("PR19")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("n × (n − 1) ÷ 2", "7 application", "trame 64 à 1 518 octets", "ARP", "non routable",
                   "un domaine de collision par port", "NAT", "Test-NetConnection -Port", "service ="):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "NetBEUI présenté comme routable" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr19(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR19_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and 'class="jc-pr-console"' in html
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200
    for theory in ("ampcr-mc13", "ampcr-mc14", "ampcr-mc21", "ampcr-mc23"):
        assert client.get(f"/uaa/{theory}").status_code == 200, theory


def test_practical_home_and_matrix_show_pr19(client, db_session):
    _pr19(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"21 cours publiés sur 30 prévus", _text(home))
    for req in REQ:
        assert plan.requirement_status(req, {"PR19"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr19(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR19"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr19(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR19", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr19(db_session)
    for _ in range(2):  # 20 exercices : deux sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

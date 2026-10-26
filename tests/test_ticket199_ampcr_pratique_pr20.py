"""Ticket #199 — AMPCR pratique écrite, PR20 « IPv4, MAC, masques et passerelles — configuration
et diagnostics écrits ».

Couvre : calculs IPv4 (réseau, diffusion, plage, nombre d'hôtes, masque ↔ préfixe, même
sous-réseau, types d'adresses) **recalculés ici indépendamment** du module `ipaddress` (arithmétique
entière) et comparés à des valeurs écrites à la main ; adresses MAC (bits I/G et U/L) ; plans
d'adressage (erreurs détectées, plan de référence sans erreur) ; sorties de commandes fictives
cohérentes avec la configuration ; schémas SVG (réseau de référence, bits /24 /26 /27, arbres de
diagnostic, accessibilité) ; réponses auto-corrigées ; contenu du cours (matière 1-15, 5 cas
résolus, 20 exercices, mini-examen) ; banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr20_bank import (
    E01_CORRECT,
    E01_MASKS,
    E02_FACTS,
    E03_ADDRESSES,
    E03_CORRECT,
    E04_CORRECT,
    E04_PAIRS,
    E05_A_SEES_B,
    E05_B_SEES_A,
    E06_PREFIXES,
    E07_BITS,
    E12_ERRORS,
    E13_ERRORS,
    E14_ERRORS,
    E17_SHOWN,
    EXAM_ITEMS,
    KIND_CALC,
    KIND_CONFIG,
    KIND_DIAGNOSIS,
    KIND_REPORT,
    PRACTICE_ITEMS,
    X01_FACTS,
    X08_PLAN,
    validate_items,
)
from app.v1.ampcr_pratique_pr20_course import PR20_TITLE, pr20_course_sections
from app.v1.ampcr_pratique_pr20_figures import (
    ADDRESS_KINDS,
    BITS_FIGURES,
    DIALOG_FIGURE,
    IPCONFIG_FIGURE,
    LADDER_STEPS,
    LAN_FIGURE,
    LAN_HOSTS,
    LAN_PLAN,
    LAN_POOL,
    LAN_ROUTER,
    LAN_SERVER,
    LINUX_FIGURE,
    MAC_EXAMPLE,
    MAC_RANDOM_EXAMPLE,
    PR20_FIGURES,
    STATIC_EXAMPLE,
    TREE_FIGURES,
    AddressPlan,
    Host,
    address_kind,
    host_errors,
    ip_addr_lines,
    ip_route_lines,
    ipconfig_all_lines,
    is_contiguous_mask,
    mac_is_group,
    mac_is_locally_administered,
    mask_to_prefix,
    plan_errors,
    prefix_to_mask,
    same_subnet,
    smallest_prefix_for,
    subnet_facts,
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

SLUG = "ampcr-pratique-pr20"


# --- Calcul IPv4 indépendant (arithmétique entière, sans `ipaddress`) ---------------------------


def _to_int(address: str) -> int:
    a, b, c, d = (int(x) for x in address.split("."))
    assert all(0 <= x <= 255 for x in (a, b, c, d))
    return (a << 24) | (b << 16) | (c << 8) | d


def _to_str(value: int) -> str:
    return ".".join(str((value >> s) & 255) for s in (24, 16, 8, 0))


def _mask(prefix: int) -> int:
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF


def _independent(address: str, prefix: int) -> tuple[str, str, str, str, int]:
    net = _to_int(address) & _mask(prefix)
    bcast = net | (~_mask(prefix) & 0xFFFFFFFF)
    return _to_str(net), _to_str(bcast), _to_str(net + 1), _to_str(bcast - 1), (bcast - net + 1) - 2


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_text() -> str:
    return _text(" ".join(c for _t, c in pr20_course_sections())).lower()


def _pr20(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR20")
    return module, uaa


# =============================================================================================
# 1. Calculs d'adressage
# =============================================================================================

# Valeurs écrites à la main (cahier des charges : /24, /26, /27 et compagnie).
HAND_CHECKED = {
    ("192.168.10.77", 24): ("192.168.10.0", "192.168.10.255", "192.168.10.1", "192.168.10.254", 254),
    ("192.168.10.77", 26): ("192.168.10.64", "192.168.10.127", "192.168.10.65", "192.168.10.126", 62),
    ("192.168.10.77", 27): ("192.168.10.64", "192.168.10.95", "192.168.10.65", "192.168.10.94", 30),
    ("172.16.5.200", 26): ("172.16.5.192", "172.16.5.255", "172.16.5.193", "172.16.5.254", 62),
    ("10.0.12.37", 27): ("10.0.12.32", "10.0.12.63", "10.0.12.33", "10.0.12.62", 30),
    ("192.168.1.130", 25): ("192.168.1.128", "192.168.1.255", "192.168.1.129", "192.168.1.254", 126),
    ("192.168.7.19", 28): ("192.168.7.16", "192.168.7.31", "192.168.7.17", "192.168.7.30", 14),
    ("10.20.30.140", 26): ("10.20.30.128", "10.20.30.191", "10.20.30.129", "10.20.30.190", 62),
    ("192.168.0.1", 30): ("192.168.0.0", "192.168.0.3", "192.168.0.1", "192.168.0.2", 2),
}


@pytest.mark.parametrize(("address", "prefix"), list(HAND_CHECKED))
def test_subnet_facts_match_hand_and_independent_calculation(address, prefix):
    f = subnet_facts(address, prefix)
    got = (f.network, f.broadcast, f.first_host, f.last_host, f.usable)
    assert got == HAND_CHECKED[(address, prefix)] == _independent(address, prefix)
    assert f.total == 2 ** (32 - prefix) and f.mask == _to_str(_mask(prefix))


def test_masks_prefixes_and_contiguity():
    expected = {24: "255.255.255.0", 25: "255.255.255.128", 26: "255.255.255.192", 27: "255.255.255.224",
                28: "255.255.255.240", 30: "255.255.255.252", 31: "255.255.255.254", 32: "255.255.255.255"}
    for prefix, mask in expected.items():
        assert prefix_to_mask(prefix) == mask and mask_to_prefix(mask) == prefix
    for bad in ("255.255.255.160", "255.255.0.255", "255.255.255.208", "0.255.255.255"):
        assert not is_contiguous_mask(bad)
        with pytest.raises(ValueError):
            mask_to_prefix(bad)
    assert subnet_facts("10.0.0.0", 31).usable == 2 and subnet_facts("10.0.0.1", 32).usable == 1


def test_address_kinds():
    expected = {
        "10.45.2.1": "Privée", "172.20.0.9": "Privée", "172.31.255.254": "Privée", "192.168.0.254": "Privée",
        "172.32.0.9": "Publique", "172.15.255.1": "Publique", "192.169.1.1": "Publique", "11.0.0.1": "Publique",
        "169.254.12.7": "Lien local", "127.0.0.1": "Bouclage", "127.5.5.5": "Bouclage", "0.0.0.0": "Non spécifiée",
    }
    for address, kind in expected.items():
        assert address_kind(address).startswith(kind), address


def test_same_subnet_and_sizing():
    for a, b, p in E04_PAIRS:
        independent = (_to_int(a) & _mask(p)) == (_to_int(b) & _mask(p))
        assert same_subnet(a, p, b, p) is independent
    assert not same_subnet("192.168.1.10", 24, "192.168.1.130", 25)  # masques différents
    assert [smallest_prefix_for(n) for n in (2, 14, 15, 30, 31, 62, 254)] == [30, 28, 27, 27, 26, 26, 24]


def test_mac_bits():
    assert not mac_is_group(MAC_EXAMPLE) and not mac_is_locally_administered(MAC_EXAMPLE)
    assert mac_is_locally_administered(MAC_RANDOM_EXAMPLE) and not mac_is_group(MAC_RANDOM_EXAMPLE)
    for second_digit in "26AE":
        assert mac_is_locally_administered(f"0{second_digit}-00-00-00-00-01")
    assert mac_is_group("01-00-5E-00-00-01")


def test_reference_lan_is_consistent():
    assert plan_errors(LAN_PLAN) == []
    with_nas = AddressPlan(LAN_PLAN.network, (*LAN_HOSTS, STATIC_EXAMPLE), LAN_ROUTER, LAN_SERVER, LAN_POOL)
    assert plan_errors(with_nas) == []
    assert not LAN_PLAN.in_pool(STATIC_EXAMPLE.ip)
    for host in LAN_HOSTS:
        assert (_to_int(host.ip) & _mask(24)) == _to_int("192.168.10.0")
        assert host.dhcp == LAN_PLAN.in_pool(host.ip) or host.ip in (LAN_ROUTER, LAN_SERVER)


def test_host_and_plan_errors_detect_each_fault():
    ok = Host("P", "poste", "192.168.1.10", 24, "192.168.1.1", ("192.168.1.1",), "00-11-22-33-44-55")
    assert host_errors(ok) == []
    assert "réseau" in host_errors(Host("P", "p", "192.168.1.0", 24, "192.168.1.1", (), "00-11-22-33-44-55"))[0]
    assert "diffusion" in host_errors(Host("P", "p", "192.168.1.255", 24, "192.168.1.1", (), "00-11-22-33-44-55"))[0]
    assert "hors du réseau" in host_errors(Host("P", "p", "192.168.1.130", 25, "192.168.1.1", (), "00-11-22-33-44-55"))[0]
    assert "APIPA" in host_errors(Host("P", "p", "169.254.3.4", 16, None, (), "00-11-22-33-44-55"))[0]
    joined = " ".join(E14_ERRORS)
    for fault in ("PC-B : 192.168.20.0 est l'adresse du réseau", "PC-C : adresse 192.168.20.10 déjà attribuée à PC-A",
                  "Imprimante : adresse fixe 192.168.20.60 dans l'étendue", "NAS : masque 255.255.0.0",
                  "PC-D : passerelle 192.168.21.254 hors du réseau", "Portable : 192.168.20.255 est l'adresse de diffusion"):
        assert fault in joined, fault
    assert not any(e.startswith(("PC-A", "Routeur")) for e in E14_ERRORS)
    assert any("doublon" in e for e in E12_ERRORS) and any("étendue DHCP" in e for e in E12_ERRORS)
    assert E13_ERRORS == [] and plan_errors(X08_PLAN) == []


def test_command_outputs_follow_the_configuration():
    pc = next(h for h in LAN_HOSTS if h.name == "PC-04")
    addr = "\n".join(ip_addr_lines(pc))
    assert f"inet {pc.ip}/24 brd 192.168.10.255" in addr and "link/ether 52:54:00:3a:7c:11" in addr
    route = "\n".join(ip_route_lines(pc))
    assert f"default via {LAN_ROUTER}" in route and "192.168.10.0/24 dev enp3s0" in route
    no_gw = Host("L", "p", "192.168.10.104", 24, None, (), pc.mac)
    assert "default" not in "\n".join(ip_route_lines(no_gw))
    win = "\n".join(ipconfig_all_lines(next(h for h in LAN_HOSTS if h.name == "PC-01")))
    assert "255.255.255.0" in win and f"Passerelle défaut. : {LAN_ROUTER}" in win and f"Serveur DHCP . . . : {LAN_SERVER}" in win
    apipa = "\n".join(ipconfig_all_lines(Host("A", "p", "169.254.37.112", 16, None, (), pc.mac, dhcp=True), apipa=True))
    assert "autoconfig" in apipa and "255.255.0.0" in apipa and "Bail" not in apipa
    for line in (*ipconfig_all_lines(next(h for h in LAN_HOSTS if h.name == "PC-01")), *ip_addr_lines(pc), *ip_route_lines(pc)):
        assert len(line) <= 56, line  # lisible dans l'écran fictif de 380 px


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_lan_figure_shows_every_host_with_its_addresses():
    for host in LAN_HOSTS:
        assert f"{host.ip}/{host.prefix}" in LAN_FIGURE.svg and host.mac in LAN_FIGURE.svg
        assert host.ip in LAN_FIGURE.alt
    assert LAN_FIGURE.svg.count("port ") == len(LAN_HOSTS)
    assert "203.0.113.45" in LAN_FIGURE.svg  # plage de documentation RFC 5737


def test_bits_figures_are_computed():
    assert [f.key for f in BITS_FIGURES] == ["pr20-bits-24", "pr20-bits-26", "pr20-bits-27"]
    for figure, (prefix, network, broadcast) in zip(
        BITS_FIGURES, ((24, "192.168.10.0", "192.168.10.255"), (26, "192.168.10.64", "192.168.10.127"),
                       (27, "192.168.10.64", "192.168.10.95")), strict=True,
    ):
        assert network in figure.svg and broadcast in figure.svg and f"réseau : {prefix} bits" in figure.svg
        # 4 lignes de bits réseau en gras + le titre « réseau : n bits ».
        assert figure.svg.count('font-weight="700" fill="#1f5fbf">') == prefix * 4 + 1


def test_diagnostic_trees_and_ladder():
    assert {f.key for f in TREE_FIGURES} == {"pr20-arbre-dns", "pr20-arbre-apipa", "pr20-arbre-deux-postes"}
    assert [name for name, _d in LADDER_STEPS][2:4] == ["ping 127.0.0.1", "ping de sa propre IP"]
    assert "ICMP" in TREE_FIGURES[2].alt and "pas une panne d'Internet" in TREE_FIGURES[0].alt


def test_captures_show_exact_values():
    assert "192.168.10.101(préféré)" in IPCONFIG_FIGURE.svg
    assert "brd 192.168.10.255" in LINUX_FIGURE.svg and "default via 192.168.10.1" in LINUX_FIGURE.svg
    for value in (STATIC_EXAMPLE.ip, "255.255.255.0", LAN_ROUTER, LAN_SERVER):
        assert value in DIALOG_FIGURE.svg


def test_figures_valid_accessible_and_unique():
    assert len(PR20_FIGURES) >= 12
    keys = [f.key for f in PR20_FIGURES]
    assert len(set(keys)) == len(keys)
    for figure in PR20_FIGURES:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "<title" in html and "<desc" in html and "schéma non officiel" in html
        assert 'viewBox="0 0 380' in figure.svg  # largeur mobile


# =============================================================================================
# 3. Exercices et mini-examen
# =============================================================================================


def test_items_valid_and_counts_match_ticket():
    assert validate_items() == []
    assert len(PRACTICE_ITEMS) >= 18
    kinds = [i.kind for i in PRACTICE_ITEMS]
    assert kinds.count(KIND_CALC) >= 6
    assert kinds.count(KIND_DIAGNOSIS) >= 5
    assert kinds.count(KIND_CONFIG) >= 4
    assert kinds.count(KIND_REPORT) >= 3
    assert len(EXAM_ITEMS) == 10 and sum(i.total_points for i in EXAM_ITEMS) == 20
    assert {i.question_type for i in EXAM_ITEMS} <= {"short_answer", "long_answer", "document_analysis"}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(set(keys)) == len(keys)
    assert all("AP-30" in i.requirement_ids for i in PRACTICE_ITEMS + EXAM_ITEMS)
    # Le mini-examen varie : calculs, diagnostics, configuration, compte rendu.
    assert sum(1 for i in EXAM_ITEMS if i.documents) >= 3


def test_auto_corrected_answers_are_technically_right():
    categories = ["/24", "/25", "/26", "/27", "/28", "/30", "invalide"]
    assert [categories[i] for i in E01_CORRECT] == ["/26", "/24", "/30", "invalide", "/28", "/25", "/27", "invalide"]
    assert len(E01_MASKS) == 8
    expected_kinds = ["Privée", "Privée", "Publique", "Privée", "Publique", "Lien local", "Bouclage", "Non spécifiée"]
    assert [ADDRESS_KINDS[i].split(" (")[0] for i in E03_CORRECT] == expected_kinds
    assert len(E03_ADDRESSES) == 8
    assert E04_CORRECT == (0, 1, 0, 1, 0, 1, 0, 1)
    assert E05_A_SEES_B and not E05_B_SEES_A
    assert E06_PREFIXES == (27, 28, 30, 26)
    assert E07_BITS == ("01001101", "11100000", "01000000", 64)
    for facts in E02_FACTS:
        assert (facts.network, facts.broadcast) == _independent(facts.address, facts.prefix)[:2]
    assert (X01_FACTS.network, X01_FACTS.broadcast, X01_FACTS.usable) == ("10.20.30.128", "10.20.30.191", 62)
    item = next(i for i in PRACTICE_ITEMS if i.key == "E17")
    assert [item.ordering.steps[i].split(" :")[0] for i in item.ordering.correct] == [n for n, _d in LADDER_STEPS]
    assert list(E17_SHOWN) != list(range(len(LADDER_STEPS)))


def test_every_ipv4_written_anywhere_is_valid():
    everything = " ".join(c for _t, c in pr20_course_sections()) + " ".join(
        " ".join((i.context, *i.instructions, *i.correction, *(c.expected for c in i.criteria),
                  *(d.content_text for d in i.documents)))
        for i in PRACTICE_ITEMS + EXAM_ITEMS
    )
    found = re.findall(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])", everything)
    assert len(found) > 200
    found = [a for a in found if a != "192.168.10.256"]  # contre-exemple volontaire du cours (3.1)
    for address in found:
        assert all(0 <= int(x) <= 255 for x in address.split(".")), address


def test_no_false_technical_claims_anywhere():
    text = _course_text()
    assert "172.16.0.0/12" in text and "172.31.255.255" in text and "169.254.0.0/16" in text
    assert "il n'y a pas de commande universelle" in text
    assert "passerelle ≠ dns" in text and "mac ≠ ip" in text
    assert "pas une preuve" in text or "jamais une preuve" in text
    assert "icmp" in text and "pare-feu" in text
    for wrong in ("172.32.0.0 est privée", "apipa prouve", "/27 = 255.255.255.240", "/26 = 255.255.255.224"):
        assert wrong not in text


def test_no_acronym_question_and_full_context():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        text = " ".join((item.title, item.context, *item.instructions))
        assert not re.search(r"que signifie|que veut dire|développe[rz]? l'acronyme", text, re.IGNORECASE), item.key
        assert len(item.context) >= 150, item.key


def test_items_content_matches_existing_question_types():
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        content = item_content(item, [1, 2][: len(item.documents)])
        validate_content(item.question_type, 1, content)


def test_five_resolved_cases_and_exam_not_in_course():
    text = _text(" ".join(c for _t, c in pr20_course_sections()))
    for case in ("Cas 1 — Deux PC dans des sous-réseaux différents", "Cas 2 — Un poste en APIPA",
                 "Cas 3 — Un DNS erroné", "Cas 4 — Un masque incorrect", "Cas 5 — Un doublon d'adresse IP"):
        assert case in text, case
    course = " ".join(content for _title, content in pr20_course_sections())
    for item in EXAM_ITEMS:
        assert item.context not in course and escape(item.context) not in course, item.key
    for item in PRACTICE_ITEMS:
        assert escape(item.context) in course, item.key


# =============================================================================================
# 4. Cours : toute la matière obligatoire (points 1 à 15 du ticket)
# =============================================================================================


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr20_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # 1 réseau local
        "carte réseau", "interface", "ethernet", "wi-fi", "switch", "routeur", "passerelle", "serveur dhcp",
        "serveur dns", "physique", "logique",
        # 2 MAC
        "48 bits", "hexadécimaux", "unicité administrative", "mac aléatoires", "virtuelles", "mac ≠ identité",
        # 3 IPv4
        "32 bits", "quatre octets", "décimale pointée", "unicast", "diffusion", "127.0.0.1", "10.0.0.0/8",
        "192.168.0.0/16", "169.254.0.0/16", "apipa", "0.0.0.0", "non spécifiée",
        # 4 masque
        "255.255.255.0", "/24", "/25", "/26", "/27", "/28", "/30", "/31", "/32", "et logique",
        "nombre total d'adresses", "hôtes usuels",
        # 5 CIDR
        "cidr", "contigu", "même sous-réseau",
        # 6 passerelle
        "passerelle par défaut", "route locale", "route par défaut",
        # 7 DNS
        "résolution", "par nom",
        # 8 DHCP
        "discover", "offer", "request", "acknowledge", "bail", "réservation dhcp", "statique",
        # 9 Windows
        "ipconfig /all", "ipconfig /release", "ipconfig /renew", "tracert", "nslookup", "arp -a", "route print",
        # 10 Linux
        "ip addr", "ip route", "ip neigh", "resolvectl", "networkmanager", "netplan", "temporaire", "persistante",
        # 11 plan
        "plan d'adressage", "doublon", "étendue dhcp",
        # 12 connexion directe
        "auto mdi-x", "deux couches distinctes",
        # 13 diagnostic
        "ping 127.0.0.1", "constat", "hypothèse", "résultat", "action",
        # 14 cas d'erreur
        "ip dupliquée", "mauvais masque", "mauvaise passerelle", "dns erroné", "dhcp absent",
        "sous-réseaux incompatibles", "câble débranché", "carte désactivée", "mauvaise interface", "pare-feu icmp",
        # 15 compte rendu
        "plan avant / après", "commandes et observations", "tests de validation", "risques et recommandations",
        # encadrés et glossaire
        "à retenir", "piège fréquent", "méthode examen", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_complements_and_fictive_supports():
    text = _text(" ".join(c for _t, c in pr20_course_sections()))
    for req in ("AP-30", "AP-C01"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucun n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    for mc in ("/uaa/ampcr-mc16", "/uaa/ampcr-mc17", "/uaa/ampcr-mc18", "/uaa/ampcr-mc19", "/uaa/ampcr-mc20"):
        assert mc in " ".join(c for _t, c in pr20_course_sections())


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr20_course_sections()]
    assert kinds.count("exam") == 1 and kinds.count("exercise") == 1 and kinds.count("example") == 1
    assert kinds[-1] == "info" and "summary" in kinds and "warning" in kinds


# =============================================================================================
# 5. Banque, seed et intégration au moteur
# =============================================================================================


def test_plan_slot_and_requirements():
    slot = plan.COURSE_SLOTS_BY_CODE["PR20"]
    assert slot.ticket == 199 and slot.title == PR20_TITLE == PRACTICAL_COURSES_BY_CODE["PR20"].title
    assert set(slot.requirement_ids) == {"AP-30"}
    assert "adresses MAC" in plan.REQUIREMENTS_BY_ID["AP-30"].text


def test_seed_publishes_pr20_in_practical_module_idempotently(db_session):
    module, uaa = _pr20(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR20_TITLE
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR20").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr20_course_sections())
    assert {"PR06", "PR11", "PR15", "PR16", "PR20"} <= set(plan.published_uaas(db_session))
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr20(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr20_specific():
    context = _pedagogical_context_for("PR20")
    assert context is get_practical_context("PR20")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    assert "172.16.0.0/12" in notions and "/27 .224 (30)" in notions and "APIPA" in notions
    assert "172.32.x.x est privée" in context.constraints and "mot-clé" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr20(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert len(ids) == len(set(ids)) and set(ids) >= {f"fig-{f.key}" for f in PR20_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html


def test_practical_home_and_matrix_show_pr20(client, db_session):
    _pr20(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and "5 cours publiés" in home
    assert plan.requirement_status("AP-30", {"PR20"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr20(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR20"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr20(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR20", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr20(db_session)
    for _ in range(2):  # 20 exercices : deux sessions de 10 couvrent toute la réserve
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

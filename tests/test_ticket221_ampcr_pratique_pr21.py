"""Ticket #221 — AMPCR pratique écrite, PR21 « Connexion directe de deux PC et mini-réseau ».

Couvre : données de référence et calculs **recontrôlés ici** indépendamment (câble droit ou
croisé selon MDI / MDI-X et Auto MDI-X, brochage du câble croisé, adressage de la connexion
directe, résultat d'un ping selon le lien, le réseau, le poste distant et le pare-feu, plans
d'adressage, carte des adresses, ordre du diagnostic) ; relevés fictifs (format, largeur,
statistiques) ; schémas SVG (validité, accessibilité, données dessinées, schémas à compléter
sans leurs réponses, fichiers statiques) ; exercices et mini-examen (format du socle, classements
et remises en ordre auto-corrigés, nombres des corrigés) ; cours (matière du ticket, 3
procédures, 5 cas résolus, liens, supports fictifs, cartes) ; banque, seed, pages et sessions.
Aucun appel IA réel : `FakeAIProvider` partout."""

import ipaddress
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
from app.v1.ampcr_pratique_pr21_bank import (
    E15_FREE,
    E18_ERRORS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_ACCEPT,
    KIND_ADDR,
    KIND_CABLE,
    KIND_DIAG,
    KIND_ORDER,
    KIND_SCHEMA,
    KIND_SHARE,
    PRACTICE_ITEMS,
    REQ,
    X03_LINES,
    validate_items,
)
from app.v1.ampcr_pratique_pr21_course import CASES, PR21_SLUG, PR21_TITLE, pr21_course_sections
from app.v1.ampcr_pratique_pr21_figures import (
    ACCEPT_STEPS,
    ADDRESS_RANGES,
    BOX_HOSTS,
    BOX_IP,
    BOX_PLAN,
    CABLE_ANY,
    CABLE_CROSS,
    CABLE_STRAIGHT,
    CHECK_KEYS,
    CHECKS,
    CROSSOVER_LINKS,
    D_FIREWALL,
    D_OK,
    D_PEER,
    DIRECT_STEPS,
    EXTEND_STEPS,
    ISOLATED_HOSTS,
    OUT_FAILURE,
    OUT_REPLY,
    OUT_TIMEOUT,
    OUT_UNREACHABLE,
    PC_A,
    PC_B,
    POOL,
    PR21_FIGURES,
    PROCEDURES,
    SCREEN_WIDTH,
    STATIC_FIGURES,
    Host,
    all_capture_lines,
    cable_needed,
    checks_from,
    direct_errors,
    first_failure,
    link_up,
    ping_lines,
    ping_outcome,
    ping_stats,
    plan_errors,
    range_of,
    same_network,
    static_svg,
    validation_diagnosis,
)
from app.v1.ampcr_pratique_visuals import T568A, T568B, render_figure, validate_figure
from app.v1.models import Question, QuestionnaireSession, SessionMode
from app.v1.question_engine import validate_content
from app.v1.session_service import _pedagogical_context_for, available_session_lengths
from tests.test_ticket94_french_fr06_10 import (
    _answer_all_and_submit,
    _patch_fake_provider,
    _start_session,
)

SLUG = "ampcr-pratique-pr21"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr21_course_sections())


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


def _pr21(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR21")
    return module, uaa


def _local(a: str, prefix: int, b: str) -> bool:
    return ipaddress.ip_address(b) in ipaddress.ip_network(f"{a}/{prefix}", strict=False)


# =============================================================================================
# 1. Données de référence et calculs, recontrôlés indépendamment
# =============================================================================================


def test_cable_rules_and_crossover_pinout():
    mdi = {"PC", "Portable", "Serveur", "Imprimante réseau", "Routeur (port routé)"}
    for a in ("PC", "Switch", "Hub", "Routeur (port routé)", "Box (ports LAN du switch intégré)"):
        for b in ("PC", "Switch", "Hub", "Portable", "Box (ports LAN du switch intégré)"):
            same = (a in mdi) == (b in mdi)
            assert cable_needed(a, b) == (CABLE_CROSS if same else CABLE_STRAIGHT), (a, b)
            for auto in ((True, False), (False, True), (True, True)):
                assert cable_needed(a, b, auto_a=auto[0], auto_b=auto[1]) == CABLE_ANY
                assert link_up(CABLE_STRAIGHT, a, b, auto_a=auto[0], auto_b=auto[1])
                assert link_up(CABLE_CROSS, a, b, auto_a=auto[0], auto_b=auto[1])
            assert link_up(CABLE_STRAIGHT, a, b) is not same and link_up(CABLE_CROSS, a, b) is same
    # croisé T568A ↔ T568B : 1↔3, 2↔6, le reste droit
    assert dict(CROSSOVER_LINKS) == {1: 3, 2: 6, 3: 1, 4: 4, 5: 5, 6: 2, 7: 7, 8: 8}
    for pin_a, pin_b in CROSSOVER_LINKS:
        assert T568A[pin_a - 1] == T568B[pin_b - 1]


def test_direct_connection_addressing():
    assert (PC_A.ip, PC_A.prefix, PC_B.ip, PC_B.prefix) == ("192.168.10.1", 24, "192.168.10.2", 24)
    assert PC_A.gateway is None and PC_B.gateway is None and PC_A.dns == PC_B.dns == ()
    assert PC_A.mask == PC_B.mask == "255.255.255.0"
    assert same_network(PC_A, PC_B) and direct_errors(PC_A, PC_B) == []
    other = Host("X", "", "192.168.1.2", 24, None, (), "00-11-22-33-44-55")
    slash25 = Host("Y", "", "192.168.10.130", 25, None, (), "00-11-22-33-44-56")
    dup = Host("Z", "", PC_A.ip, 24, None, (), "00-11-22-33-44-57")
    assert not same_network(PC_A, other) and direct_errors(PC_A, other)
    assert _local(PC_A.ip, 24, slash25.ip) and not _local(slash25.ip, 25, PC_A.ip)
    assert not same_network(PC_A, slash25) and direct_errors(PC_A, slash25)
    assert any("doublon" in e for e in direct_errors(PC_A, dup))


def test_ping_outcomes_follow_the_network_model():
    other = Host("X", "", "192.168.1.2", 24, None, (), "00-11-22-33-44-55")
    slash25 = Host("Y", "", "192.168.10.130", 25, None, (), "00-11-22-33-44-56")
    assert ping_outcome(PC_A, PC_B.ip, PC_B) == OUT_REPLY
    assert ping_outcome(PC_A, PC_B.ip, PC_B, link=False) == OUT_FAILURE
    assert ping_outcome(other, PC_A.ip, PC_A) == OUT_FAILURE  # hors réseau, pas de passerelle
    assert ping_outcome(PC_A, "192.168.10.7", None) == OUT_UNREACHABLE
    assert ping_outcome(PC_A, PC_B.ip, PC_B, dst_on=False) == OUT_UNREACHABLE
    assert ping_outcome(PC_A, PC_B.ip, PC_B, icmp_allowed=False) == OUT_TIMEOUT
    assert ping_outcome(PC_A, slash25.ip, slash25) == OUT_TIMEOUT  # la réponse ne sait pas repartir
    assert ping_outcome(slash25, PC_A.ip, PC_A) == OUT_FAILURE
    routed = Host("R", "", "192.168.10.9", 24, "192.168.10.254", (), "00-11-22-33-44-58")
    with pytest.raises(ValueError):
        ping_outcome(routed, "198.51.100.20", None)


def test_ping_captures_statistics_and_width():
    ok = ping_lines(PC_A, PC_B.ip, OUT_REPLY)
    assert ping_stats(ok) == (4, 4, 0) and "TTL=128" in ok[3]
    timeout = ping_lines(PC_B, PC_A.ip, OUT_TIMEOUT)
    assert ping_stats(timeout) == (4, 0, 4) and "perte 100%" in timeout[-1]
    unreachable = ping_lines(PC_A, "192.168.10.9", OUT_UNREACHABLE)
    # comme Windows : réponse du poste lui-même, comptée comme reçue (0 % de perte)
    assert ping_stats(unreachable) == (4, 4, 0) and f"Réponse de {PC_A.ip} : Impossible de joindre" in unreachable
    failure = ping_lines(PC_A, PC_B.ip, OUT_FAILURE)
    assert failure.count("PING : échec de la transmission. Défaillance générale.") == 4 and "perte 100%" in failure[-1]
    assert X03_LINES == ping_lines(PC_A, "192.168.10.2", OUT_UNREACHABLE)
    every_console = [line for i in PRACTICE_ITEMS + EXAM_ITEMS for d in i.documents if d.kind == "console"
                     for line in d.content_text.splitlines()]
    for line in (*all_capture_lines(), *every_console):
        assert len(line) <= SCREEN_WIDTH, line


def test_mini_network_plans_and_address_map():
    assert 3 <= len(ISOLATED_HOSTS) <= 6 and 3 <= len(BOX_HOSTS) - 1 <= 6
    assert [h.ip for h in ISOLATED_HOSTS] == [f"192.168.10.{n}" for n in range(1, 6)]
    assert all(h.gateway is None and h.prefix == 24 for h in ISOLATED_HOSTS)
    assert plan_errors(BOX_PLAN) == []
    low, high = (ipaddress.ip_address(a) for a in POOL)
    for host in BOX_HOSTS:
        inside = low <= ipaddress.ip_address(host.ip) <= high
        assert inside is host.dhcp, host.name  # adresses fixes hors étendue, DHCP dans l'étendue
        if host.ip != BOX_IP:
            assert host.gateway == BOX_IP and host.dns == (BOX_IP,)
    covered = [n for a, b, _l in ADDRESS_RANGES for n in range(a, b + 1)]
    assert covered == list(range(1, 255))  # .1 à .254, sans trou ni chevauchement
    assert range_of(BOX_IP).startswith("Box") and range_of("192.168.10.150") == "Étendue DHCP de la box"
    assert range_of("192.168.10.20").startswith("Imprimantes")
    for bad in ("192.168.10.0", "192.168.10.255", "192.168.11.4"):
        with pytest.raises(ValueError):
            range_of(bad)
    assert len(E18_ERRORS) == 4 and E15_FREE == "192.168.10.6"


def test_diagnosis_order():
    for key, _what, diagnosis in CHECKS:
        assert validation_diagnosis(first_failure(key)) == diagnosis
    assert validation_diagnosis(dict.fromkeys(CHECK_KEYS, True)) == D_OK
    assert validation_diagnosis(checks_from(PC_B, PC_A, icmp_allowed=False)) == D_FIREWALL
    assert validation_diagnosis(checks_from(PC_B, PC_A, peer_on=False)) == D_PEER
    assert validation_diagnosis(checks_from(PC_B, PC_A)) == D_OK


def test_procedures_order():
    assert [label for label, _d in DIRECT_STEPS][:3] == ["Vérifier le matériel", "Brancher et lire les voyants", "Adresser les deux PC"]
    assert DIRECT_STEPS[-1][0] == "Consigner" and EXTEND_STEPS[2][0] == "Établir le plan d'adressage"
    assert len(ACCEPT_STEPS) == len(CHECK_KEYS) + 1 and ACCEPT_STEPS[-1][0] == "Consigner et faire signer"
    assert len(PROCEDURES) == 3


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    all_figures = PR21_FIGURES + tuple(f for f, _p in STATIC_FIGURES)
    keys = [f.key for f in all_figures]
    assert len(keys) == len(set(keys)) == 16 and len(PR21_FIGURES) >= 4  # ticket : ≥ 4 schémas
    for figure in all_figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR21_FIGURES}
    direct = by_key["pr21-connexion-directe"].svg
    for value in (PC_A.ip, PC_B.ip, "255.255.255.0", "Passerelle : (vide)", PC_A.mac, PC_B.mac):
        assert value in direct, value
    cables = by_key["pr21-droit-ou-croise"].svg
    rows = re.findall(r'data-cable="([^"]+)"', cables)
    assert rows.count(escape(CABLE_CROSS)) == 4 and rows.count(escape(CABLE_STRAIGHT)) == 2 and rows.count(escape(CABLE_ANY)) == 1
    ping = by_key["pr21-ping-arp"].svg
    assert "perdus = 0 (perte 0%)" in ping and PC_B.mac.lower() in ping
    firewall = by_key["pr21-ping-pare-feu"].svg
    assert "Délai d&#x27;attente de la demande dépassé." in firewall and PC_A.mac.lower() in firewall
    box = by_key["pr21-mini-reseau-box"].svg
    for host in BOX_HOSTS:
        assert host.ip in box, host.name
    assert re.findall(r'data-range="([^"]+)"', by_key["pr21-plan-adressage"].svg) == [f"{a}-{b}" for a, b, _l in ADDRESS_RANGES]
    for key, (_title, steps) in zip(("pr21-procedure-connexion", "pr21-procedure-extension", "pr21-procedure-recette"),
                                    PROCEDURES, strict=True):
        for index, (label, _d) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in by_key[key].svg, (key, label)


def test_schemas_to_complete_hide_their_answers():
    by_key = {f.key: f.svg for f, _p in STATIC_FIGURES}
    direct = by_key["pr21-connexion-a-completer"]
    assert PC_B.ip not in direct and "Droit ou croisé" not in direct and 'data-cable=""' in direct
    assert direct.count("255.255.255.0") == 1 and all(f"{n} ?" in direct for n in "①②③④")
    cables = by_key["pr21-cablage-a-completer"]
    assert "Câble croisé" not in cables and "Câble droit" not in cables and "Auto MDI-X)" not in cables
    mini = by_key["pr21-mini-reseau-a-completer"]
    assert "192.168.10.20/" not in mini and ">Switch<" not in mini and "passerelle 192.168.10.254" not in mini
    addr = by_key["pr21-plan-adressage-a-completer"]
    for hidden in ("Postes et serveur", "Imprimantes", "Étendue DHCP", "Box :"):
        assert hidden not in addr, hidden


def test_static_figure_files_are_the_generated_svg():
    assert len(STATIC_FIGURES) == 4
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
    assert kinds.count(KIND_SCHEMA) == 4
    for kind in (KIND_ORDER, KIND_CABLE, KIND_ADDR, KIND_DIAG, KIND_SHARE, KIND_ACCEPT):
        assert kind in kinds
    schema_images = {d.image for i in PRACTICE_ITEMS for d in i.documents if d.image}
    assert schema_images == {p for _f, p in STATIC_FIGURES}
    # ticket : exercices avec plans et sorties de commandes
    assert sum(1 for i in PRACTICE_ITEMS if any(d.kind == "console" for d in i.documents)) >= 5
    assert sum(1 for i in PRACTICE_ITEMS if any(d.kind in ("tableau", "schéma") for d in i.documents)) >= 6
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    covered = {r for i in PRACTICE_ITEMS + EXAM_ITEMS for r in i.requirement_ids}
    assert covered == REQ == set(plan.COURSE_SLOTS_BY_CODE["PR21"].requirement_ids)
    types = [i.question_type for i in PRACTICE_ITEMS]
    assert types.count("ordering") == 3 and types.count("classification") == 5


def test_auto_corrected_answers():
    def ordered(key: str) -> list[str]:
        item = _item(key)
        return [item.ordering.steps[i].split(" — ")[0] for i in item.ordering.correct]

    assert ordered("E01") == [label for label, _d in DIRECT_STEPS]
    assert ordered("E02") == [label for label, _d in EXTEND_STEPS]
    assert ordered("E03") == [label for label, _d in ACCEPT_STEPS]

    def find(key: str, needle: str) -> str:
        c = _item(key).classification
        index = next(i for i, e in enumerate(c.elements) if needle in e)
        return c.categories[c.correct[index]]

    assert find("E04", "Deux anciens PC") == CABLE_CROSS and find("E04", "PC récent") == CABLE_ANY
    assert find("E04", "switch 10/100") == CABLE_STRAIGHT and find("E04", "port routé") == CABLE_CROSS
    assert find("E04", "box") == CABLE_STRAIGHT and find("E04", "deux anciens switchs".capitalize()) == CABLE_CROSS
    assert find("E05", "Imprimante").startswith("Adresse fixe") and find("E05", "Tablette").endswith("(DHCP de la box)")
    assert find("E05", "en direct").startswith("Adresse fixe")
    assert find("E06", "Média déconnecté").startswith("Liaison") and find("E06", "169.254.40.12").startswith("DHCP")
    assert find("E06", "(Dupliqué)") == "Adresse IP dupliquée" and find("E06", "255.255.255.128").startswith("Plan")
    assert find("E07", "arp -a montre") == D_FIREWALL and find("E07", "éteint") == D_PEER
    assert find("E07", "Accès refusé").startswith("Partage") and find("E07", "DNS vide").startswith("Internet")
    assert find("E08", "câble débranché") == OUT_FAILURE and find("E08", "éteint") == OUT_UNREACHABLE
    assert find("E08", "/25") == OUT_TIMEOUT and find("E08", "référence") == OUT_REPLY
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

    assert PC_B.ip in text("E09") and "255.255.255.0" in text("E09") and "Vide" in text("E09")
    assert "192.168.10.128/25" in text("E13") and "Défaillance générale" in text("E13") and "Délai" in text("E13")
    assert "192.168.10.6" in text("E15") and "PC-C" in text("E15")
    assert "169.254" in text("E16") and "4 erreurs" in text("E18")
    assert "198.51.100.20" in text("E19") and BOX_IP in text("E19")
    assert "0 %" in text("X03") and PC_A.ip in text("X03")
    assert "192.168.1.0/24" in text("X04") and "étendue" in text("X06").lower()
    assert "la plus restrictive" in text("X09") and "Lecture" in text("X09")


def test_schema_documents_point_to_static_files():
    item = _item("E09")
    layout = _document_layout(item.documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr21-connexion-a-completer.svg"
    assert "PC-A" in layout["alt"] and "non officiel" in layout["notice"]


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("câble croisé", "câble droit", "auto mdi-x", "192.168.10.1", "192.168.10.2", "255.255.255.0",
                  "passerelle", "ping", "arp -a", "pare-feu", "profil", "partage", "permissions", "switch",
                  "dhcp", "dns", "plan d'adressage", "(dupliqué)", "169.254", "masque", "recette"):
        assert right in text, right
    for wrong in ("désactiver le pare-feu suffit", "le switch distribue les adresses", "passerelle obligatoire",
                  "câble droit entre deux cartes sans auto mdi-x fonctionne", "0 % de perte prouve"):
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
    assert len(CASES) == 5
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
    for figure in PR21_FIGURES:
        assert f'id="fig-{figure.key}"' in course, figure.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr21_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "carte réseau", "câble droit", "câble croisé", "historique", "auto mdi-x", "voyant de lien",
        "192.168.10.1", "192.168.10.2", "/24", "masque", "aucune passerelle", "réseau isolé", "ping", "arp",
        "pare-feu", "permissions", "partage", "3 à 6 pc", "switch", "dhcp", "statique", "routeur", "passerelle",
        "dns", "plan d'adressage", "dupliqué", "masque", "liaison", "mise en service", "recette",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    for req in ("AP-28", "AP-38"):
        assert req in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "rfc 5737" in text.lower()
    for link in ("/uaa/ampcr-mc15", "/uaa/ampcr-mc16", "/uaa/ampcr-pratique-pr15", "/uaa/ampcr-pratique-pr18",
                 "/uaa/ampcr-pratique-pr19", "/uaa/ampcr-pratique-pr20", "/uaa/ampcr-pratique-pr24",
                 f"/uaa/{PR21_SLUG}/practice", f"/uaa/{PR21_SLUG}/exam"):
        assert link in raw, link
    for unpublished in ("/uaa/ampcr-pratique-pr22", "/uaa/ampcr-pratique-pr23", "/uaa/ampcr-pratique-pr25"):
        assert unpublished not in raw, unpublished
    anchors = set(re.findall(r'id="(pr21-e\d\d)"', raw))
    assert anchors == {f"pr21-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr21-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr21_course_sections()]
    assert kinds[:10] == ["theory"] * 10
    assert kinds[10:] == ["example", "warning", "exercise", "exam", "summary", "info"]


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR21"]
    assert slot.ticket == 221 and slot.title == PR21_TITLE == PRACTICAL_COURSES_BY_CODE["PR21"].title


# =============================================================================================
# 5. Seed, banque, correction
# =============================================================================================


def test_seed_publishes_pr21_in_practical_module_idempotently(db_session):
    module, uaa = _pr21(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR21_TITLE and uaa.position == 21
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR21").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr21_course_sections())
    assert {"PR20", "PR21", "PR24"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR20") < ordered.index("PR21") < ordered.index("PR24")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr21(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr21_specific():
    context = _pedagogical_context_for("PR21")
    assert context is get_practical_context("PR21")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("Auto MDI-X", "T568A ↔ T568B", "192.168.10.1/24", "compté comme reçu", "profil Public",
                   "la plus restrictive", "hors de l'étendue DHCP", "(Dupliqué)"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "désactivation du pare-feu" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr21(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR21_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and 'class="jc-pr-console"' in html
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200
    for theory in ("ampcr-mc15", "ampcr-mc16"):
        assert client.get(f"/uaa/{theory}").status_code == 200, theory


def test_practical_home_and_matrix_show_pr21(client, db_session):
    _pr21(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR22 (#222) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR21"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr21(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR21"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr21(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR21", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr21(db_session)
    for _ in range(2):  # 20 exercices : deux sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

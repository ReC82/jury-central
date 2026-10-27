"""Ticket #224 — AMPCR pratique écrite, PR25 « Wi-Fi : configuration, couverture, sécurité et
diagnostic ».

Couvre : données de référence et calculs **recontrôlés ici** indépendamment (fréquences et
chevauchement des canaux 2,4 GHz, choix du canal, canaux 5 et 6 GHz par largeur, affaiblissement
en espace libre et obstacles, qualité Windows en %, débit derrière un répéteur, modes de
sécurité, contrôle des clés, audit d'une configuration, ordre du diagnostic) ; relevés fictifs
(format, largeur) ; schémas SVG (validité, accessibilité, données dessinées, schémas à compléter
sans leurs réponses, fichiers statiques) ; exercices et mini-examen (format du socle,
classements et remises en ordre auto-corrigés, valeurs des corrigés) ; cours (matière du
ticket, 3 procédures, 5 cas résolus, liens, supports fictifs, cartes) ; banque, seed, pages et
sessions. Aucun appel IA réel : `FakeAIProvider` partout."""

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
from app.v1.ampcr_pratique_pr25_bank import (
    E04_CASES,
    E05_CASES,
    E11_BEST,
    E11_NEIGHBORS,
    E17_CONFIG,
    E17_FIXED,
    E17_ISSUES,
    E18_KEYS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    KIND_CONFIG,
    KIND_DIAG,
    KIND_ORDER,
    KIND_SCHEMA,
    PRACTICE_ITEMS,
    REQ,
    X01_BEST,
    X05_5,
    X05_24,
    X06_MBPS,
    X09_BEST,
    validate_items,
)
from app.v1.ampcr_pratique_pr25_course import (
    C1_AUDIT,
    C1_CHANNEL,
    C4_CHANNEL,
    CASES,
    PR25_SLUG,
    PR25_TITLE,
    pr25_course_sections,
)
from app.v1.ampcr_pratique_pr25_figures import (
    BAND_5,
    BAND_6,
    BAND_24,
    BANDS,
    CONFIG_STEPS,
    COVERAGE_STEPS,
    EU_5_CHANNELS,
    EU_6_CHANNELS,
    NEIGHBORS,
    NEIGHBORS_BEST,
    NON_OVERLAP_24,
    PR25_FIGURES,
    PROCEDURES,
    REFERENCE_CONFIG,
    REPEATER_BAD,
    REPEATER_GOOD,
    SCREEN_WIDTH,
    SEC_BEST,
    SEC_MIN,
    SEC_REFUSE,
    SECURITY_BY_NAME,
    STATIC_FIGURES,
    SURVEY,
    SURVEY_BY_KEY,
    TROUBLE_STEPS,
    W_CHANNEL,
    W_INTERNET,
    W_INVISIBLE,
    W_IP,
    W_KEY,
    W_OK,
    W_REPEATER,
    W_SIGNAL,
    WIFI_KEYS,
    ApConfig,
    Neighbor,
    WifiState,
    all_capture_lines,
    audit_config,
    best_channel_24,
    blocks_5,
    blocks_6,
    center_5,
    center_6,
    center_24,
    dbm_from_pct,
    drivers_lines,
    first_failure,
    fspl_db,
    interference_24,
    link_rate,
    networks_lines,
    nmcli_lines,
    overlaps_24,
    passphrase_issues,
    quality_pct,
    repeater_mbps,
    signal_verdict,
    static_svg,
    useful_mbps,
    wifi_checks,
    wifi_diagnosis,
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

SLUG = "ampcr-pratique-pr25"
STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course_raw() -> str:
    return " ".join(c for _t, c in pr25_course_sections())


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


def _pr25(db_session) -> tuple[Module, UAA]:
    seed()
    module = db_session.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    uaa = next(u for u in module.uaas if u.code == "PR25")
    return module, uaa


# =============================================================================================
# 1. Données de référence et calculs, recontrôlés indépendamment
# =============================================================================================


def test_channel_frequencies_and_overlap():
    assert [center_24(c) for c in (1, 6, 11, 13, 14)] == [2412, 2437, 2462, 2472, 2484]
    with pytest.raises(ValueError):
        center_24(15)
    assert NON_OVERLAP_24 == (1, 6, 11)
    # ~22 MHz occupés : chevauchement si les centres sont à moins de 22 MHz d'écart
    for a in range(1, 14):
        for b in range(1, 14):
            assert overlaps_24(a, b) == (abs(center_24(a) - center_24(b)) < 22), (a, b)
    assert not any(overlaps_24(a, b) for a in NON_OVERLAP_24 for b in NON_OVERLAP_24 if a != b)
    assert overlaps_24(7, 11) and overlaps_24(3, 6) and overlaps_24(3, 1) and not overlaps_24(6, 11)
    assert center_5(36) == 5180 and center_5(140) == 5700 and center_6(1) == 5955 and center_6(93) == 6415


def test_best_channel_recomputed_by_hand():
    # Référence de l'atelier : 1 gêné par la boulangerie (−58) et le canal 3 (−71) ; 6 par le canal 3 ;
    # 11 par la Livebox du canal 13 (−79) ; le cabinet à −88 ne compte pas.
    assert interference_24(1, NEIGHBORS) == (2, -58)
    assert interference_24(6, NEIGHBORS) == (1, -71)
    assert interference_24(11, NEIGHBORS) == (1, -79)
    assert NEIGHBORS_BEST == 11
    # E11 : le voisin du canal 7 gêne le 11 → canal 1
    assert {n.ssid: n.channel for n in E11_NEIGHBORS}["WiFi-Voisin"] == 7 and E11_BEST == 1
    assert (X01_BEST, X09_BEST, C1_CHANNEL, C4_CHANNEL) == (11, 11, 1, 6)
    assert best_channel_24((Neighbor("x", 6, -90),)) == 1  # aucun voisin fort : plus petit canal


def test_5_and_6_ghz_channels_per_width():
    assert len(EU_5_CHANNELS) == 19 and 144 not in EU_5_CHANNELS and 149 not in EU_5_CHANNELS
    assert [len(blocks_5(w)) for w in (20, 40, 80, 160)] == [19, 9, 4, 2]
    assert blocks_5(80) == ((36, 40, 44, 48), (52, 56, 60, 64), (100, 104, 108, 112), (116, 120, 124, 128))
    assert blocks_5(160) == ((36, 40, 44, 48, 52, 56, 60, 64), (100, 104, 108, 112, 116, 120, 124, 128))
    assert (140,) in blocks_5(20) and not any(140 in b for b in blocks_5(40))
    # 6 GHz : 5945–6425 MHz = 480 MHz = 24 canaux de 20 MHz
    assert len(EU_6_CHANNELS) == (6425 - 5945) // 20 == 24
    assert [len(blocks_6(w)) for w in (20, 40, 80, 160)] == [24, 12, 6, 3]
    assert center_6(EU_6_CHANNELS[0]) - 10 == 5945 and center_6(EU_6_CHANNELS[-1]) + 10 == 6425


def test_path_loss_signal_and_quality():
    # FSPL = 20 log d + 20 log f − 27,55 (d m, f MHz)
    assert fspl_db(1, 2437) == pytest.approx(40.19, abs=0.01)
    assert fspl_db(15, 5180) - fspl_db(15, 2437) == pytest.approx(20 * math.log10(5180 / 2437))
    for p in SURVEY:
        for band, f, index in ((BAND_24, 2437, 0), (BAND_5, 5180, 1)):
            loss = {"vitre": (2, 3), "cloison": (3, 4), "brique": (6, 10), "béton": (12, 18), "dalle": (15, 25),
                    "métal": (20, 25)}
            expected = round(20 - (20 * math.log10(p.distance_m) + 20 * math.log10(f) - 27.55)
                             - sum(loss[o][index] for o in p.obstacles))
            assert p.dbm(band) == expected, (p.key, band)
            assert p.dbm(BAND_5) < p.dbm(BAND_24)
    assert [SURVEY_BY_KEY[k].dbm(BAND_24) for k in ("P1", "P2", "P3", "P4", "P5")] == [-36, -46, -52, -77, -53]
    assert [SURVEY_BY_KEY[k].dbm(BAND_5) for k in ("P1", "P2", "P3", "P4", "P5")] == [-42, -57, -64, -95, -70]
    assert [signal_verdict(v) for v in (-50, -60, -61, -67, -68, -75, -76)] == [
        "excellent", "excellent", "bon", "bon", "faible", "faible", "insuffisant"]
    assert [quality_pct(v) for v in (-40, -50, -74, -77, -100, -110)] == [100, 100, 52, 46, 0, 0]
    assert dbm_from_pct(46) == -77 and dbm_from_pct(100) == -50
    assert (X05_24, X05_5) == (-56, -70)


def test_throughput_and_repeater():
    assert [link_rate(v) for v in (-55, -62, -70, -80, -90)] == [144, 104, 52, 13, 0]
    assert useful_mbps(144) == 72 and useful_mbps(144, 4) == 18
    assert repeater_mbps(-80, -30) == pytest.approx(13 / 2 / 2)
    assert (REPEATER_BAD.uplink_dbm, REPEATER_GOOD.uplink_dbm) == (-80, -54)
    assert REPEATER_BAD.client_dbm > REPEATER_GOOD.client_dbm  # le mal placé a le meilleur signal… vers le client
    assert (REPEATER_BAD.mbps, REPEATER_GOOD.mbps) == (3.25, 36.0)
    assert X06_MBPS == 3.25


def test_security_keys_and_audit():
    verdicts = {name: m.verdict for name, m in SECURITY_BY_NAME.items()}
    assert verdicts == {"Ouvert": SEC_REFUSE, "WEP": SEC_REFUSE, "WPA": SEC_REFUSE, "WPA2-Personnel": SEC_MIN,
                        "WPA2/WPA3-Personnel": SEC_MIN, "WPA3-Personnel": SEC_BEST, "WPA2/WPA3-Entreprise": SEC_BEST}
    assert SECURITY_BY_NAME["WPA2-Personnel"].cipher == "AES-CCMP" and SECURITY_BY_NAME["WEP"].cipher == "RC4"
    assert passphrase_issues("court") and passphrase_issues("x" * 64)
    assert passphrase_issues("Kx7#qT2m") == ("trop courte (moins de 12 caractères)",)
    assert passphrase_issues("baguette brioche eclair tartelette") == ()
    assert "contient le nom du réseau ou de l'entreprise" in passphrase_issues("Boulangerie-Lenoir-2026!",
                                                                               names=("Lenoir",))
    accepted = [k for k in E18_KEYS if not passphrase_issues(k, names=("LENOIR-WIFI", "Lenoir", "Boulangerie"))]
    assert accepted == ["P@in-Croissant-Four-Levain", "baguette brioche eclair tartelette"]
    assert audit_config(REFERENCE_CONFIG) == () and C1_AUDIT == () and audit_config(E17_FIXED) == ()
    assert [p for p, _c in E17_ISSUES] == ["Sécurité", "Clé", "WPS", "Administration", "Micrologiciel",
                                           "Canal 2,4 GHz", "Largeur 2,4 GHz", "SSID masqué", "Invités"]
    assert E17_CONFIG.security == "WPA"
    assert audit_config(ApConfig("BUREAU-X", "WPA3-Personnel", "Longue-Phrase-De-Test-26", dhcp_sources=2)) == (
        ("DHCP", "une seule source DHCP par réseau (répéteur en mode point d'accès ou pont)"),)


def test_wifi_diagnosis_order():
    assert WIFI_KEYS == ("visible", "auth", "ip", "internet", "signal", "repeteur", "canal")
    assert wifi_diagnosis(wifi_checks(WifiState())) == W_OK
    cases = {
        WifiState(radio_on=False): W_INVISIBLE,
        WifiState(ssid_broadcast=False): W_INVISIBLE,
        WifiState(band_supported=False): W_INVISIBLE,
        WifiState(signal_dbm=-90): W_INVISIBLE,
        WifiState(key_ok=False): W_KEY,
        WifiState(security_supported=False): W_KEY,
        WifiState(address_ok=False): W_IP,
        WifiState(dns_ok=False): W_INTERNET,
        WifiState(wan_ok=False): W_INTERNET,
        WifiState(signal_dbm=-72): W_SIGNAL,
        WifiState(repeater_uplink_dbm=-79): W_REPEATER,
        WifiState(strong_overlaps=2): W_CHANNEL,
        WifiState(key_ok=False, address_ok=False, strong_overlaps=3): W_KEY,  # le premier échec l'emporte
    }
    for state, expected in cases.items():
        assert wifi_diagnosis(wifi_checks(state)) == expected, state
    for key, expected in zip(WIFI_KEYS, (W_INVISIBLE, W_KEY, W_IP, W_INTERNET, W_SIGNAL, W_REPEATER, W_CHANNEL),
                             strict=True):
        assert wifi_diagnosis(first_failure(key)) == expected


def test_procedures_order():
    assert CONFIG_STEPS[0][0] == "Placer" and CONFIG_STEPS[-1][0] == "Tester et consigner"
    assert [label for label, _d in COVERAGE_STEPS].index("Câbler si possible") < [
        label for label, _d in COVERAGE_STEPS].index("Sinon mesh ou répéteur")
    assert [label for label, _d in TROUBLE_STEPS] == [
        "Constater", "Réseau visible ?", "Clé et sécurité", "Adresse", "Internet", "Signal et répéteur", "Canal",
        "Corriger et consigner"]
    assert len(PROCEDURES) == 3


def test_captures_format_and_width():
    lines = (*all_capture_lines(), *networks_lines(tuple((n.ssid, "WPA2 - Personnel", n) for n in E11_NEIGHBORS)),
             *nmcli_lines((("RESTO-CUISINE", 3, 64, "WPA2"),)), *drivers_lines("802.11b 802.11g 802.11n", BAND_24))
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        for document in item.documents:
            if document.kind == "console":
                lines += tuple(document.content_text.splitlines())
    assert all(len(line) <= SCREEN_WIDTH for line in lines), [line for line in lines if len(line) > SCREEN_WIDTH]
    scan = networks_lines((("ATELIER-PRO", "WPA2 - Personnel", Neighbor("x", 6, -58, "aa")),))
    assert "         Signal      : 84%" in scan and "         Canal       : 6" in scan and "         Bande       : 2,4 GHz" in scan
    assert networks_lines((("X", "WPA2 - Personnel", Neighbor("x", 44, -58, "aa")),))[5].endswith("5 GHz")


# =============================================================================================
# 2. Schémas
# =============================================================================================


def test_figures_valid_accessible_and_unique():
    all_figures = PR25_FIGURES + tuple(f for f, _p in STATIC_FIGURES)
    keys = [f.key for f in all_figures]
    assert len(keys) == len(set(keys)) == 17
    for figure in all_figures:
        assert validate_figure(figure) == [], figure.key
        html = str(render_figure(figure))
        assert 'role="img"' in html and "(schéma non officiel)" in html and not figure.official


def test_figures_drawn_from_data():
    by_key = {f.key: f for f in PR25_FIGURES}
    channels = by_key["pr25-canaux-24"].svg
    for ch in NON_OVERLAP_24:
        assert f'data-channel="{ch}" data-center="{center_24(ch)}"' in channels
    for n in NEIGHBORS:
        assert f'data-neighbor="{n.channel}"' in channels and f"{n.ssid} : canal {n.channel}, {n.dbm} dBm" in channels
    assert f"canal {NEIGHBORS_BEST}</text>" in channels
    widths = by_key["pr25-canaux-5"].svg
    for w in (20, 40, 80, 160):
        assert widths.count(f'data-width="{w}"') == len(blocks_5(w))
    assert 'data-block="36-48"' in widths and 'data-block="132-136"' in widths
    coverage = by_key["pr25-couverture"].svg
    for p in SURVEY:
        assert f'data-point="{p.key}" data-24="{p.dbm(BAND_24)}" data-5="{p.dbm(BAND_5)}"' in coverage
    repeater = by_key["pr25-repeteur"].svg
    assert 'data-placement="mal" data-uplink="-80"' in repeater and "≈ 3,2 Mb/s utiles" in repeater
    assert 'data-placement="bien" data-uplink="-54"' in repeater and "≈ 36 Mb/s utiles" in repeater
    security = by_key["pr25-securite"].svg
    for name in SECURITY_BY_NAME:
        assert f'data-mode="{escape(name)}"' in security
    assert security.index(f'data-verdict="{SEC_BEST}"') < security.index(f'data-verdict="{SEC_REFUSE}"')
    tree = by_key["pr25-arbre-diagnostic"].svg
    assert tree.count("data-step=") == len(WIFI_KEYS)
    arch = by_key["pr25-architecture"].svg
    for node in ("box", "dhcp", "ap", "repeteur"):
        assert f'data-node="{node}"' in arch
    for key, (_title, steps) in zip(("pr25-procedure-configuration", "pr25-procedure-couverture",
                                     "pr25-procedure-depannage"), PROCEDURES, strict=True):
        for index, (label, _d) in enumerate(steps, start=1):
            assert f"{index}. {escape(label)}" in by_key[key].svg, (key, label)


def test_schemas_to_complete_hide_their_answers():
    by_key = {f.key: f.svg for f, _p in STATIC_FIGURES}
    arch = by_key["pr25-architecture-a-completer"]
    assert "passerelle, NAT" not in arch and "serveur DHCP et DNS" not in arch and "retransmet par radio" not in arch
    assert all(f"{n} ?" in arch for n in "①②③④") and 'data-node="box"' not in arch
    channels = by_key["pr25-canaux-a-completer"]
    assert "canal 1</text>" not in channels and "canal 6</text>" not in channels and "canal 11</text>" not in channels
    assert "data-channel=" not in channels and 'data-neighbor="13"' in channels and all(f"{n} ?" in channels for n in "①②③④")
    coverage = by_key["pr25-couverture-a-completer"]
    assert 'data-point="P3"' in coverage and "-52 dBm" not in coverage and "-64 dBm" not in coverage
    assert "-77 dBm" not in coverage and "-70 dBm" not in coverage and all(f"{n} ?" in coverage for n in "①②③④")
    repeater = by_key["pr25-repeteur-a-completer"]
    assert "-80 dBm" not in repeater and "-54 dBm" not in repeater and "Mb/s utiles" not in repeater


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
    assert kinds.count(KIND_SCHEMA) == 4 and KIND_ORDER in kinds
    assert kinds.count(KIND_DIAG) >= 5  # ticket : ≥ 5 diagnostics
    assert kinds.count(KIND_CONFIG) >= 4  # ticket : ≥ 4 choix de configuration
    assert sum(1 for i in PRACTICE_ITEMS if any(d.kind == "console" for d in i.documents)) >= 5  # ≥ 5 relevés
    schema_images = {d.image for i in PRACTICE_ITEMS for d in i.documents if d.image}
    assert schema_images == {p for _f, p in STATIC_FIGURES}
    keys = [i.key for i in PRACTICE_ITEMS + EXAM_ITEMS]
    assert len(keys) == len(set(keys))
    for item in PRACTICE_ITEMS + EXAM_ITEMS:
        assert REQ & set(item.requirement_ids), item.key


def test_auto_corrected_answers():
    e04 = _item("E04").classification
    assert [e04.categories[c] for c in e04.correct] == [SECURITY_BY_NAME[m].verdict for _t, m in E04_CASES]
    assert [e04.categories[c] for c in e04.correct].count(SEC_REFUSE) == 3
    e05 = _item("E05").classification
    expected = [W_INVISIBLE, W_KEY, W_IP, W_INTERNET, W_SIGNAL, W_REPEATER, W_CHANNEL, W_INVISIBLE]
    assert [e05.categories[c] for c in e05.correct] == expected and [k for _t, k in E05_CASES][-1] == "visible"
    e06 = _item("E06").classification
    assert [e06.categories[c] for c in e06.correct] == [BAND_24, BAND_24, BAND_5, BAND_5, BAND_6, BAND_24, BAND_6]
    assert e06.categories == BANDS
    e18 = _item("E18").classification
    assert [e18.categories[c] for c in e18.correct] == [
        "Clé à refuser", "Clé à refuser", "Clé acceptable", "Clé à refuser", "Clé acceptable", "Clé à refuser"]
    for key, steps in (("E01", CONFIG_STEPS), ("E03", TROUBLE_STEPS)):
        ordering = _item(key).ordering
        restored = [ordering.steps[i] for i in ordering.correct]
        assert restored == [f"{label} — {detail}" for label, detail in steps], key
    e02 = _item("E02").ordering
    assert [e02.steps[i].split(" — ")[0] for i in e02.correct] == [
        "Découverte", "Association", "Clés", "DHCP", "Passerelle et DNS"]


def test_values_in_corrections_match_calculations():
    e08 = " ".join(c.expected for c in _item("E08").criteria)
    assert "① 1" in e08 and "② 6" in e08 and "③ 11" in e08 and "④ canal 11" in e08
    e09 = " ".join(c.expected for c in _item("E09").criteria)
    assert "① -52 dBm (excellent)" in e09 and "② -64 dBm (bon)" in e09 and "③ -77 dBm (insuffisant)" in e09
    assert "④ -70 dBm (faible)" in e09
    e10 = " ".join(c.expected for c in _item("E10").criteria)
    assert "① -80 dBm (insuffisant)" in e10 and "② environ 3,2 Mb/s" in e10 and "④ environ 36 Mb/s" in e10
    assert "signal 46 % ≈ -77 dBm (insuffisant)" in _item("E12").criteria[0].expected
    assert "Canal 1" in _item("E11").criteria[1].expected
    assert "Canal 11" in _item("X01").criteria[0].expected and "canal 11" in _item("X09").criteria[1].expected.lower()
    assert "-56 dBm" in _item("X05").criteria[0].expected and "-70 dBm" in _item("X05").criteria[0].expected
    assert "≈ 3,2 Mb/s" in _item("X06").criteria[0].expected
    assert "9 défauts" in _item("E17").criteria[0].expected


def test_schema_documents_point_to_static_files():
    item = _item("E07")
    layout = _document_layout(item.documents[0])
    assert layout["kind"] == "figure" and layout["src"] == "/static/img/ampcr-pratique/pr25-architecture-a-completer.svg"
    assert "SRV-01" in layout["alt"] and "non officiel" in layout["notice"]


def test_no_false_technical_claims_anywhere():
    text = _course_text() + " " + _all_items_text().lower()
    for right in ("ssid", "bssid", "2,4 ghz", "5 ghz", "6 ghz", "1, 6", "20 mhz", "dfs", "dbm", "répéteur", "mesh",
                  "roaming", "wpa2", "wpa3", "aes-ccmp", "sae", "802.1x", "radius", "wps", "réseau invités",
                  "isolation", "dhcp", "169.254", "nslookup", "netsh wlan"):
        assert right in text, right
    for wrong in ("wep est sûr", "wep est recommandé", "tkip est recommandé", "masquer le ssid protège",
                  "le filtrage mac suffit", "canal 3 est conseillé", "40 mhz en 2,4 ghz est conseillé",
                  "le répéteur doit être placé à côté du client", "wps est sûr", "désactiver le chiffrement pour"):
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
    for figure in PR25_FIGURES:
        assert f'id="fig-{figure.key}"' in course, figure.key


def test_course_teaches_every_mandatory_point():
    titles = [t for t, _ in pr25_course_sections()]
    assert len(titles) == len(set(titles))
    text = _course_text()
    for notion in (
        # matière du ticket, dans l'ordre du cahier des charges
        "point d'accès", "client", "routeur", "répéteur", "mesh", "ssid", "bssid", "2,4 ghz", "5 ghz", "6 ghz",
        "réglementation", "canal", "largeur de canal", "interférences", "portée", "obstacles", "roaming", "débit réel",
        "association", "authentification", "dhcp", "dns", "802.11", "wep", "tkip", "obsolètes", "wpa2", "aes-ccmp",
        "wpa3", "sae", "personnel", "entreprise", "802.1x", "radius", "wps", "mot de passe fort", "réseau invités",
        "isolation", "micrologiciel", "placement", "réseau invisible", "connecté sans internet", "mauvaise clé",
        "interférence", "mauvaise adresse ip", "répéteur mal placé",
        # encadrés
        "objectifs", "procédure professionnelle", "erreur fréquente", "à l'écrit", "repère rapide", "glossaire",
    ):
        assert notion in text, notion


def test_course_flags_requirements_links_and_fictive_supports():
    raw = _course_raw()
    text = _text(raw)
    assert "AP-33" in text and "WIFI : principe, sécurisation, cryptage, répéteur" in text
    assert "Compléments pédagogiques" in text and "fictif" in text.lower()
    assert "aucune n'est une question officielle" in text.lower()
    assert "aucun schéma n'est tiré d'une image générée" in text.lower()
    assert "la mesure fait foi" in text.lower() or "la mesure sur place fait foi" in text.lower()
    for link in ("/uaa/ampcr-mc25", "/uaa/ampcr-mc26", "/uaa/ampcr-pratique-pr19", "/uaa/ampcr-pratique-pr20",
                 "/uaa/ampcr-pratique-pr23", "/uaa/ampcr-pratique-pr24", f"/uaa/{PR25_SLUG}/practice",
                 f"/uaa/{PR25_SLUG}/exam"):
        assert link in raw, link
    for unpublished in ("/uaa/ampcr-pratique-pr26", "/uaa/ampcr-pratique-ex04"):
        assert unpublished not in raw
    anchors = set(re.findall(r'id="(pr25-e\d\d)"', raw))
    assert anchors == {f"pr25-{i.key.lower()}" for i in PRACTICE_ITEMS}
    assert "(#pr25-" not in raw


def test_block_titles_give_the_expected_card_kinds():
    from app.card_kind import classify_block_title

    kinds = [classify_block_title(t) for t, _ in pr25_course_sections()]
    assert kinds[:10] == ["theory"] * 10
    assert kinds[10:] == ["example", "warning", "exercise", "exam", "summary", "info"]


def test_plan_slot_matches_ticket():
    slot = plan.COURSE_SLOTS_BY_CODE["PR25"]
    assert slot.ticket == 224 and slot.title == PR25_TITLE == PRACTICAL_COURSES_BY_CODE["PR25"].title
    assert slot.requirement_ids == ("AP-33",)


# =============================================================================================
# 5. Seed, banque, correction
# =============================================================================================


def test_seed_publishes_pr25_in_practical_module_idempotently(db_session):
    module, uaa = _pr25(db_session)
    assert uaa.slug == SLUG and uaa.is_published and uaa.title == PR25_TITLE and uaa.position == 25
    blocks = len(uaa.lesson_blocks)
    seed()
    db_session.expire_all()
    assert db_session.query(UAA).filter_by(module_id=module.id, code="PR25").count() == 1
    assert len(db_session.get(UAA, uaa.id).lesson_blocks) == blocks == len(pr25_course_sections())
    assert {"PR23", "PR24", "PR25"} <= set(plan.published_uaas(db_session))
    ordered = [u.code for u in sorted(module.uaas, key=lambda u: (u.position, u.id))]
    assert ordered.index("PR24") < ordered.index("PR25")
    theory = db_session.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)


def test_bank_import_reserves_and_documents(db_session):
    module, uaa = _pr25(db_session)
    assert PRACTICAL_BANK_IMPORTERS[SLUG] is import_practical_bank
    assert import_practical_bank(db_session, module, uaa) == len(PRACTICE_ITEMS) + len(EXAM_ITEMS)
    assert import_practical_bank(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    usages = [question_usage(q) for q in questions]
    assert usages.count("practice") == len(PRACTICE_ITEMS) and usages.count("exam") == 10


def test_correction_context_is_pr25_specific():
    context = _pedagogical_context_for("PR25")
    assert context is get_practical_context("PR25")
    assert context.course_key == SLUG
    notions = " ".join(context.allowed_notions)
    for notion in ("1, 6, 11", "DFS dès le 52", "WPA3 obligatoire", "0 % ≈ −100 dBm", "−67 bon", "divisé par deux",
                   "SAE", "802.1X/RADIUS", "WPS à désactiver", "169.254", "une seule source DHCP"):
        assert notion in notions, notion
    assert "mot-clé" in context.constraints and "WEP" in context.constraints and "WPS" in context.constraints


# =============================================================================================
# 6. Pages et sessions
# =============================================================================================


def test_course_page_renders_figures_and_exercises(client, db_session):
    _pr25(db_session)
    response = client.get(f"/uaa/{SLUG}")
    assert response.status_code == 200
    html = response.text
    ids = re.findall(r'<figure class="jc-tech-figure[^"]*" id="([^"]+)"', html)
    assert set(ids) >= {f"fig-{f.key}" for f in PR25_FIGURES}
    assert html.count('class="jc-exercise-card"') == len(PRACTICE_ITEMS)
    assert "<details open" not in html
    assert 'href="/ampcr-pratique"' in html and f"/uaa/{SLUG}/exam" in html
    assert "<table" in html and 'class="jc-pr-console"' in html
    for _figure, path in STATIC_FIGURES:
        assert client.get(f"/static/{path}").status_code == 200
    for linked in ("ampcr-mc25", "ampcr-mc26", "ampcr-pratique-pr19", "ampcr-pratique-pr20", "ampcr-pratique-pr23",
                   "ampcr-pratique-pr24"):
        assert client.get(f"/uaa/{linked}").status_code == 200, linked


def test_practical_home_and_matrix_show_pr25(client, db_session):
    _pr25(db_session)
    home = client.get("/ampcr-pratique").text
    assert f'href="/uaa/{SLUG}"' in home and re.search(r"\d+ cours publiés sur 30 prévus", _text(home))  # PR26 (#225) publié ensuite
    for req in REQ:
        assert plan.requirement_status(req, {"PR25"}) == plan.STATUS_PARTIAL
    assert plan.VALIDATED_REQUIREMENT_IDS == frozenset()
    assert client.get("/ampcr-pratique/matrice").status_code == 200


@pytest.mark.parametrize("mode", ["practice", "exam"])
def test_sessions_draw_only_from_their_reserve_without_generation(authenticated_client, db_session, monkeypatch, mode):
    fake = _patch_fake_provider(monkeypatch)
    _pr25(db_session)
    assert authenticated_client.get(f"/uaa/{SLUG}/{mode}").status_code == 200
    session_url = _start_session(authenticated_client, db_session, SLUG, mode)
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert {question_usage(sq.question_version.question) for sq in session.session_questions} == {mode}
    assert session.question_count == 10
    assert fake.questionnaire_calls == []
    assert {sq.question_version.question.uaa.code for sq in session.session_questions} == {"PR25"}
    if mode == "exam":
        page = authenticated_client.get(f"{session_url}?q=1").text
        assert "Corrigé de référence" not in page and "Barème" not in page


def test_exam_lengths_limited_and_score_on_20(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    module, uaa = _pr25(db_session)
    import_practical_bank(db_session, module, uaa)
    db_session.commit()
    from app.v1.models import User

    user = db_session.query(User).first()
    assert available_session_lengths(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="PR25", mode=SessionMode.EXAM
    ) == (10,)
    session_url = _start_session(authenticated_client, db_session, SLUG, "exam")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    html = authenticated_client.get(session_url).text
    assert "data-score-on-20" in html and "/ 20" in html


def test_practice_sessions_with_schemas_classification_and_ordering_submit(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    _pr25(db_session)
    for _ in range(2):  # 20 exercices : deux sessions de 10
        session_url = _start_session(authenticated_client, db_session, SLUG, "practice")
        _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
        assert authenticated_client.get(session_url).status_code == 200

"""Ticket #84 — Lexique AMPCR : acronymes, abréviations et vocabulaire FR/EN.

Accessible depuis Informatique → AMPCR → Lexique / Acronymes FR-EN. Ressource
pédagogique transverse, réutilisée par la garde § 83.B (`app.v1.course_coverage`) comme
source de notions autorisées en plus du cours propre à chaque MC.
"""

from app.v1.course_coverage import defined_notions_for_code
from app.v1.lexicon import LEXICON_THEMES, all_entries, lexicon_defined_notions

# Les 6 acronymes de la liste minimale du ticket volontairement ABSENTS car introuvables
# dans le programme AMPCR actuel (audit exhaustif, § 84.C).
_DELIBERATELY_EXCLUDED = {"ROM", "WLAN", "IPV6", "FTP", "CLI", "GUI"}

_TICKET_MINIMAL_LIST = {
    "CPU", "GPU", "RAM", "ROM", "PSU", "BIOS", "UEFI", "HDD", "SSD", "SATA", "NVME", "M.2",
    "SMART", "TBW", "PCIE", "USB", "LAN", "WAN", "WLAN", "IP", "IPV4", "IPV6", "MAC", "DHCP",
    "DNS", "TCP", "UDP", "OSI", "SSID", "BSSID", "RJ45", "UTP", "FTP", "STP", "VLAN", "NAT",
    "VPN", "WPA2", "WPA3", "ESD", "DEEE", "CLI", "GUI", "NTFS", "FAT32", "EXFAT",
}


# --- § 84.A : structure par thèmes -------------------------------------------------------------


def test_eleven_themes_present_in_order():
    assert len(LEXICON_THEMES) == 11
    expected_titles = [
        "1. Architecture PC", "2. Stockage", "3. BIOS / UEFI", "4. Systèmes",
        "5. Réseaux / TCP-IP / OSI", "6. Câblage / RJ45 / fibre", "7. Wi-Fi", "8. Sécurité",
        "9. Dépannage", "10. Sauvegarde / données", "11. Métier / support",
    ]
    assert [t.title for t in LEXICON_THEMES] == expected_titles


def test_every_entry_belongs_to_exactly_one_theme():
    seen = set()
    for theme in LEXICON_THEMES:
        for entry in theme.entries:
            assert entry.acronym not in seen, f"{entry.acronym} apparaît dans plusieurs thèmes"
            seen.add(entry.acronym)


# --- § 84.B : champs d'une entrée ---------------------------------------------------------------


def test_every_entry_has_definition_context_and_mc_codes():
    for entry in all_entries():
        assert entry.definition, entry.acronym
        assert entry.context, entry.acronym
        assert entry.mc_codes, entry.acronym
        assert all(code.startswith("MC") for code in entry.mc_codes)


def test_smart_entry_matches_course_content_verbatim():
    smart = next(e for e in all_entries() if e.acronym == "SMART")
    assert smart.english == "Self-Monitoring, Analysis and Reporting Technology"
    assert "MC04" in smart.mc_codes


def test_entries_with_documented_confusion_reflect_real_pieges():
    m2 = next(e for e in all_entries() if e.acronym == "M.2")
    assert m2.confusion is not None
    assert "NVMe" in m2.confusion


# --- § 84.C : liste minimale, uniquement si réellement présente dans le programme ---------------


def test_all_lexicon_acronyms_are_uppercase_unique():
    acronyms = [e.acronym.upper() for e in all_entries()]
    assert len(acronyms) == len(set(acronyms))


def test_deliberately_excluded_acronyms_are_not_in_lexicon():
    """§ 84.C : ne pas ajouter une entrée uniquement parce qu'elle est connue en
    informatique — ROM/WLAN/IPv6/FTP/CLI/GUI n'apparaissent nulle part dans
    AMPCR_COURSE_MARKDOWN ni dans les objectifs des MC (audit exhaustif), donc absents."""
    notions = lexicon_defined_notions()
    for excluded in _DELIBERATELY_EXCLUDED:
        assert excluded not in notions


def test_all_included_entries_come_from_the_ticket_minimal_list():
    notions = lexicon_defined_notions()
    assert notions <= _TICKET_MINIMAL_LIST


def test_lexicon_has_at_least_thirty_verified_entries():
    assert len(all_entries()) >= 30


# --- § 84.F : intégration avec la garde § 83.B ---------------------------------------------------


def test_lexicon_notions_available_regardless_of_mc():
    """Le lexique est une ressource transverse : ses notions sont disponibles même pour
    un MC dont le cours propre ne les couvre pas."""
    notions_mc01 = defined_notions_for_code("MC01")
    assert "SMART" in notions_mc01  # SMART n'est enseigné qu'en MC04, jamais en MC01.


def test_lexicon_closes_the_cpu_gap_found_in_ticket_83_audit():
    """CPU n'est jamais développé dans AMPCR_COURSE_MARKDOWN (audit § 83.A) — le lexique
    comble ce gap pour que « Que signifie CPU ? » reste posable sans violer § 83.B."""
    from app.v1.course_coverage import check_course_coverage_gap

    class _FakeUaa:
        code = "MC01"

    content = {"prompt": "Que signifie l'acronyme CPU ?"}
    assert check_course_coverage_gap(None, _FakeUaa(), "short_answer", content) == []


# --- Route HTTP -----------------------------------------------------------------------------


def test_lexicon_route_requires_login(client):
    response = client.get("/modules/ampcr/lexicon", follow_redirects=False)
    assert response.status_code == 303


def test_lexicon_route_renders_for_authenticated_user(authenticated_client):
    response = authenticated_client.get("/modules/ampcr/lexicon")
    assert response.status_code == 200
    assert "SMART" in response.text
    assert "Self-Monitoring, Analysis and Reporting Technology" in response.text


def test_lexicon_route_has_search_input(authenticated_client):
    response = authenticated_client.get("/modules/ampcr/lexicon")
    assert 'id="lexicon-search"' in response.text


def test_lexicon_route_has_print_button(authenticated_client):
    response = authenticated_client.get("/modules/ampcr/lexicon")
    assert "window.print()" in response.text


def test_lexicon_route_shows_mc_codes_per_entry(authenticated_client):
    response = authenticated_client.get("/modules/ampcr/lexicon")
    assert "MC04" in response.text


def test_module_detail_links_to_lexicon_for_ampcr(authenticated_client, db_session):
    from app.models import Module
    from app.seed import seed

    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    response = authenticated_client.get(f"/modules/{ampcr.slug}")
    assert response.status_code == 200
    assert "/modules/ampcr/lexicon" in response.text


def test_module_detail_does_not_link_to_lexicon_for_other_modules(authenticated_client, db_session):
    from app.models import Module
    from app.seed import seed

    seed()
    other = db_session.query(Module).filter(Module.code != "AMPCR").first()
    if other is None:
        return
    response = authenticated_client.get(f"/modules/{other.slug}")
    assert response.status_code == 200
    assert "/modules/ampcr/lexicon" not in response.text

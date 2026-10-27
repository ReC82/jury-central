"""Ticket #235 — audit final de couverture officielle et de qualité du parcours AMPCR pratique.

Garde-fous transversaux sur le contenu réellement publié (cours rendus, banques, seed) :
preuves de couverture AP-01…AP-38 (cours ET exercice ET examen blanc), « validé » jamais sans
preuve, barèmes, exactitude des adresses IPv4/masques et des brochages T568A/B écrits en
toutes lettres, séparation Théorie/Pratique, liens du parcours et de la matrice.
"""

import html
import ipaddress
import re

import pytest

from app.models import UAA, Module
from app.seed import seed
from app.v1 import ampcr_pratique_audit as audit
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ai_bridge import CORRECTABLE_TYPES
from app.v1.ampcr_pratique_bank import PRACTICAL_COURSES, PRACTICAL_COURSES_BY_CODE
from app.v1.ampcr_pratique_visuals import T568A, T568B
from app.v1.models import QuestionnaireSession
from tests.test_ticket94_french_fr06_10 import _patch_fake_provider, _start_session


def _text(markup: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup)))


def _published_texts():
    """(code, repère, texte) de tout le contenu servi : blocs de cours et questions."""
    for course in PRACTICAL_COURSES:
        yield course.code, "cours", audit.course_text(course.code)
        for item in course.items:
            parts = [item.context, *item.instructions, *item.correction]
            parts += [c.expected for c in item.criteria]
            parts += [d.content_text for d in item.documents]
            yield course.code, item.key, "\n".join(parts)


# =============================================================================================
# 1. Couverture : preuves dans le contenu publié
# =============================================================================================


def test_all_36_units_are_written_and_planned():
    assert [c.code for c in PRACTICAL_COURSES] == [f"PR{i:02d}" for i in range(1, 31)] + [
        f"EX{i:02d}" for i in range(1, 7)
    ]
    assert set(PRACTICAL_COURSES_BY_CODE) == plan.PLANNED_CODES


def test_every_requirement_has_witness_terms():
    assert set(audit.REQUIREMENT_TERMS) == set(plan.REQUIREMENTS_BY_ID)
    assert all(audit.REQUIREMENT_TERMS.values())


@pytest.mark.parametrize("requirement_id", [r.id for r in plan.ALL_REQUIREMENTS])
def test_requirement_is_proven_by_course_exercise_and_mock_exam(requirement_id):
    evidence = audit.requirement_evidence(requirement_id)
    assert evidence.course_codes and not evidence.missing_courses, requirement_id
    assert not evidence.missing_exam_codes, requirement_id
    assert not evidence.missing_terms, (requirement_id, evidence.missing_terms)
    assert evidence.practice_items, requirement_id
    assert evidence.mock_exam_items, requirement_id
    assert evidence.proven


def test_validated_set_is_exactly_the_proven_set():
    assert plan.VALIDATED_REQUIREMENT_IDS == audit.proven_requirement_ids()
    assert len([r for r in plan.VALIDATED_REQUIREMENT_IDS if r.startswith("AP-") and r[3:].isdigit()]) == 38


def test_missing_witness_term_blocks_validation(monkeypatch):
    monkeypatch.setitem(audit.REQUIREMENT_TERMS, "AP-22", ("notion-jamais-enseignee",))
    evidence = audit.requirement_evidence("AP-22")
    assert evidence.missing_terms == ("notion-jamais-enseignee",) and not evidence.proven


def test_status_needs_publication_even_when_proven():
    everything = plan.PLANNED_CODES
    assert plan.requirement_status("AP-34", everything) == plan.STATUS_VALIDATED
    assert plan.requirement_status("AP-34", everything - {"EX03"}) == plan.STATUS_PARTIAL
    assert plan.requirement_status("AP-34", set()) == plan.STATUS_TODO
    summary = plan.coverage_summary(plan.coverage_rows(everything))
    assert summary["complete"] and summary["counts"][plan.STATUS_VALIDATED] == 38
    assert not plan.coverage_summary(plan.coverage_rows(everything - {"PR17"}))["complete"]


def test_item_requirements_are_known_ids():
    for course in PRACTICAL_COURSES:
        for item in course.items:
            assert item.requirement_ids, (course.code, item.key)
            assert set(item.requirement_ids) <= set(plan.REQUIREMENTS_BY_ID), (course.code, item.key)


def test_items_cover_every_requirement_of_their_slot():
    for course in PRACTICAL_COURSES:
        slot = plan.COURSE_SLOTS_BY_CODE.get(course.code) or plan.EXERCISE_SLOTS_BY_CODE[course.code]
        covered = {r for item in course.items for r in item.requirement_ids}
        assert set(slot.requirement_ids) <= covered, course.code


# =============================================================================================
# 2. Barèmes et corrigés
# =============================================================================================


def test_scoring_is_coherent():
    for course in PRACTICAL_COURSES:
        for item in course.items:
            assert item.question_type in CORRECTABLE_TYPES, (course.code, item.key)
            assert item.criteria and all(c.points > 0 and c.expected for c in item.criteria), (course.code, item.key)
            assert item.correction, (course.code, item.key)
        exam = [i for i in course.items if i.usage == "exam"]
        if course.code.startswith("PR"):
            assert [i for i in course.items if i.usage == "practice"], course.code
            assert len(exam) == 10 and sum(i.total_points for i in exam) == 20, course.code
        elif course.variants:
            by_key = {i.key: i for i in exam}
            assert [sum(by_key[k].total_points for k in v) for v in course.variants] == [100] * len(course.variants)
        else:
            assert len(exam) == len(course.items) and sum(i.total_points for i in exam) == 100, course.code


def test_every_course_has_the_required_sections():
    expected = ("Objectifs", "Exemples", "Pièges", "Exercices corrigés", "Mini-examen noté sur 20", "Fiche mémo", "Sources")
    for course in PRACTICAL_COURSES:
        if not course.code.startswith("PR"):
            continue
        text = audit.course_text(course.code)
        for title in expected:
            assert title in text, (course.code, title)


# =============================================================================================
# 3. Exactitude technique transversale
# =============================================================================================

_IPV4 = re.compile(r"(?<![\d.])(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?:/(\d{1,2}))?(?![\d.])")
_MASK = re.compile(r"(?<![\d.])255\.\d{1,3}\.\d{1,3}\.\d{1,3}(?![\d.])")
_VALID_MASKS = {str(ipaddress.IPv4Network(f"0.0.0.0/{p}").netmask) for p in range(33)}
# Contre-exemples volontaires, présentés comme invalides dans leur contexte (PR20).
_DELIBERATE_INVALID = {
    ("PR20", "192.168.10.256"),
    ("PR20", "255.255.255.160"),
    ("PR20", "255.255.0.255"),
    ("PR20", "255.255.255.208"),
}


def test_ipv4_addresses_prefixes_and_masks_are_valid():
    checked = 0
    for code, key, raw in _published_texts():
        text = _text(raw)
        for match in _IPV4.finditer(text):
            checked += 1
            octets = [int(x) for x in match.groups()[:4]]
            if any(o > 255 for o in octets):
                assert (code, match.group(0)) in _DELIBERATE_INVALID, (code, key, match.group(0))
            if match.group(5):
                assert int(match.group(5)) <= 32, (code, key, match.group(0))
        for match in _MASK.finditer(text):
            if match.group(0) not in _VALID_MASKS:
                assert (code, match.group(0)) in _DELIBERATE_INVALID, (code, key, match.group(0))
    assert checked > 3000


def test_deliberate_invalid_examples_are_flagged_as_invalid():
    text = _text(audit.course_text("PR20"))
    for _code, value in _DELIBERATE_INVALID:
        if value == "255.255.255.208":
            continue  # question X02 : masque à faire corriger par le candidat
        window = text[text.index(value) - 200: text.index(value) + 200]
        assert re.search(r"invalide|pas\W+des masques valides|n'est", window), value


_COLOUR = r"(?:\d\s*[:=]?\s*)?(blanc[-/ ]?(?:orange|vert|bleu|marron)|orange|vert|bleu|marron)"
_T568_SEQUENCE = re.compile(
    r"T568([AB])\W{0,20}(?:(?!blanc)[a-zé ]{0,25}\W{0,5})?" + "".join([_COLOUR + r"\s*[,;]?\s*"] * 8),
    re.IGNORECASE,
)


def test_every_written_t568_sequence_matches_the_standard():
    reference = {"A": list(T568A), "B": list(T568B)}
    checked = 0
    for code, key, raw in _published_texts():
        for match in _T568_SEQUENCE.finditer(_text(raw)):
            colours = [re.sub(r"blanc[-/ ]?", "blanc-", c.lower()) for c in match.groups()[1:]]
            assert colours == reference[match.group(1).upper()], (code, key, match.group(0))
            checked += 1
    assert checked >= 20


def test_reference_pinouts_and_coax_values():
    assert T568A == ("blanc-vert", "vert", "blanc-orange", "bleu", "blanc-bleu", "orange", "blanc-marron", "marron")
    assert T568B == ("blanc-orange", "orange", "blanc-vert", "bleu", "blanc-bleu", "vert", "blanc-marron", "marron")
    pr16 = audit.course_text("PR16")
    for fact in ("50 Ω", "185 m", "RG-58", "75 Ω"):
        assert fact in pr16, fact
    assert re.search(r"10BASE2[^.]{0,80}50 Ω", pr16)


# =============================================================================================
# 4. Publication, séparation Théorie/Pratique et navigation
# =============================================================================================


@pytest.fixture()
def seeded(db_session):
    seed()
    return db_session


def test_seed_publishes_all_36_units_in_the_practical_module_only(seeded):
    published = plan.published_uaas(seeded)
    assert set(published) == plan.PLANNED_CODES
    theory = seeded.query(Module).filter_by(code="AMPCR").one()
    assert all(u.code.startswith("MC") for u in theory.uaas)
    practical = seeded.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    assert all(u.code[:2] in {"PR", "EX"} for u in practical.uaas)
    for code, uaa in published.items():
        assert uaa.slug == f"ampcr-pratique-{code.lower()}"
        assert len(seeded.get(UAA, uaa.id).lesson_blocks) > 0


def test_matrix_shows_38_validated_with_evidence(client, seeded):
    response = client.get("/ampcr-pratique/matrice")
    assert response.status_code == 200
    text = _text(response.text)
    assert "38 exigences officielles — 38 validée(s), 0 partielle(s), 0 non traitée(s)" in text
    assert "Couverture complète." in text
    assert "Preuves (audit)" in text and "validation pédagogique finale reste celle du propriétaire" in text
    assert "Notion absente du cours" not in text
    for req in plan.ALL_REQUIREMENTS:
        assert f'id="{req.id}"' in response.text


def test_practical_navigation_links_resolve(client, seeded):
    home = client.get("/ampcr-pratique")
    assert home.status_code == 200
    assert "30 cours publiés sur 30 prévus" in _text(home.text)
    links = set(re.findall(r'href="(/(?:ampcr-pratique|uaa/ampcr-pratique-)[^"#?]*)', home.text))
    for code in plan.PLANNED_CODES:
        assert f"/uaa/ampcr-pratique-{code.lower()}" in links, code
    for link in sorted(links):
        assert client.get(link).status_code == 200, link
    for code in sorted(plan.PLANNED_CODES):
        page = client.get(f"/uaa/ampcr-pratique-{code.lower()}")
        assert page.status_code == 200, code
        assert "/ampcr-pratique" in page.text, code  # retour au parcours Pratique écrite


def test_practical_session_autosaves_resumes_and_hides_the_correction(authenticated_client, seeded, monkeypatch):
    _patch_fake_provider(monkeypatch)
    slug = "ampcr-pratique-pr15"
    session_url = _start_session(authenticated_client, seeded, slug, mode="practice")
    session = seeded.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    practical = seeded.query(Module).filter_by(code=plan.PRACTICAL_MODULE_CODE).one()
    assert session.module_id == practical.id  # progression du parcours Pratique, jamais de la Théorie
    written = next(
        sq for sq in sorted(session.session_questions, key=lambda sq: sq.position)
        if sq.question_version.question_type in {"short_answer", "long_answer", "document_analysis"}
    )
    response = authenticated_client.post(
        f"/api/v1/sessions/{session.id}/answers/{written.id}", json={"answer_json": {"text": "brouillon PR15"}}
    )
    assert response.status_code == 200 and response.json() == {"saved": True}
    seeded.expire_all()
    saved = next(sq for sq in seeded.get(QuestionnaireSession, session.id).session_questions if sq.id == written.id)
    assert saved.answer.answer_json["text"] == "brouillon PR15"
    page = authenticated_client.get(f"{session_url}?q={written.position}").text
    assert "brouillon PR15" in page  # reprise exacte de la réponse sauvegardée
    assert "Corrigé de référence" not in page and "Barème" not in page
    landing = authenticated_client.get(f"/uaa/{slug}/practice").text
    assert "Reprendre l'entraînement en cours" in landing and session_url in landing

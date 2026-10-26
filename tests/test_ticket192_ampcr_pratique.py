"""Ticket #192 — socle du parcours AMPCR pratique écrite (cycle 2026-2027/1) et matrice de
couverture officielle. Aucune IA, aucun contenu seedé : le plan est lu tel quel."""

import re
from dataclasses import replace

import pytest

from app.models import UAA, Module, Subject
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_plan import AMPCR_PLAN_BY_CODE
from app.v1.ampcr_pratique_format import (
    EXAMPLE_EXERCISE,
    to_question_content,
    validate_exercise,
)
from app.v1.models import create_question, create_source_document


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


# --- Matrice : exhaustivité et traçabilité -------------------------------------------------


def test_official_requirements_cover_pages_5_and_6_without_omission():
    officials = plan.OFFICIAL_REQUIREMENTS
    assert len(officials) == 38  # 18 puces p. 5 + 20 puces p. 6
    assert sum(1 for r in officials if r.page == 5) == 18
    assert sum(1 for r in officials if r.page == 6) == 20
    assert [r.id for r in officials] == [f"AP-{i:02d}" for i in range(1, 39)]
    assert officials[0].text == "La structure d’un ordinateur, ses composants et ses périphériques."
    assert officials[-1].text == "Création d’un mini réseau entre plusieurs machines."
    texts = " ".join(r.text for r in officials)
    for notion in ("UTP, FTP, STP, Coax", "impédance", "RJ45 (code des couleurs)", "BNC",
                   "fibre optique", "WIFI : principe, sécurisation, cryptage, répéteur",
                   "groupe de travail", "NETBEUI", "UEFI", "défragmentation"):
        assert notion in texts


def test_requirement_ids_unique_and_complements_flagged():
    ids = [r.id for r in plan.ALL_REQUIREMENTS]
    assert len(ids) == len(set(ids))
    assert all(r.kind == plan.KIND_OFFICIAL and r.page for r in plan.OFFICIAL_REQUIREMENTS)
    assert all(r.kind == plan.KIND_COMPLEMENT and r.page is None for r in plan.COMPLEMENT_REQUIREMENTS)


def test_every_requirement_has_a_planned_course_and_exercise():
    for req in plan.ALL_REQUIREMENTS:
        assert plan.courses_for_requirement(req.id), req.id
        assert plan.exercises_for_requirement(req.id), req.id
    referenced = {r for c in plan.COURSE_SLOTS for r in c.requirement_ids}
    assert referenced <= set(plan.REQUIREMENTS_BY_ID)


def test_slots_pr01_pr30_ex01_ex06_in_six_modules():
    assert [c.code for c in plan.COURSE_SLOTS] == [f"PR{i:02d}" for i in range(1, 31)]
    assert [e.code for e in plan.EXERCISE_SLOTS] == [f"EX{i:02d}" for i in range(1, 7)]
    assert len(plan.MODULES) == 6
    assert sum(len(m.course_codes) for m in plan.MODULES) == 30
    assert {m.exercise_code for m in plan.MODULES} == {e.code for e in plan.EXERCISE_SLOTS}


def test_theory_links_point_to_existing_mc_courses():
    for req in plan.ALL_REQUIREMENTS:
        for code in req.theory_codes:
            assert code in AMPCR_PLAN_BY_CODE, (req.id, code)


def test_status_never_validated_without_course_exercise_and_explicit_validation(monkeypatch):
    req = "AP-04"  # PR04 + EX01
    assert plan.requirement_status(req, set()) == plan.STATUS_TODO
    assert plan.requirement_status(req, {"PR04"}) == plan.STATUS_PARTIAL
    assert plan.requirement_status(req, {"PR04", "EX01"}) == plan.STATUS_PARTIAL
    monkeypatch.setattr(plan, "VALIDATED_REQUIREMENT_IDS", frozenset({req}))
    assert plan.requirement_status(req, {"PR04"}) == plan.STATUS_PARTIAL
    assert plan.requirement_status(req, {"PR04", "EX01"}) == plan.STATUS_VALIDATED
    summary = plan.coverage_summary(plan.coverage_rows({"PR04", "EX01"}))
    assert summary["complete"] is False


def test_official_source_traced():
    assert plan.OFFICIAL_SOURCE.url.endswith("26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf")
    assert re.fullmatch(r"[0-9a-f]{64}", plan.OFFICIAL_SOURCE.sha256)
    assert "345/2007/249" in plan.PROGRAMME_SOURCE.version
    day = " ".join(p for s in plan.DAY_INSTRUCTIONS for p in s.paragraphs)
    assert "L’EXAMEN SE FERA UNIQUEMENT PAR ÉCRIT." in day
    assert "50% (10/20)" in day
    assert "calculatrice (non programmable)" in day
    assert not re.search(r"\b\d+\s*(?:h|heures?|minutes?)\b", day)  # aucune durée inventée


# --- Format d'exercice ---------------------------------------------------------------------


def test_example_exercise_is_valid_and_maps_to_existing_type(db_session):
    assert validate_exercise(EXAMPLE_EXERCISE) == []
    assert EXAMPLE_EXERCISE.total_points == 10
    subject = Subject(name="Informatique", slug="informatique")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="AMPCR", slug="ampcr", subject_id=subject.id)
    db_session.add(module)
    db_session.flush()
    document = EXAMPLE_EXERCISE.documents[0]
    source = create_source_document(
        db_session, title=document.title, content_text=document.content_text, module_id=module.id
    )
    content = to_question_content(EXAMPLE_EXERCISE, [source.current_version_id])
    assert content["max_score"] == 10
    assert "Barème sur 10 points" in content["rubric"]
    question = create_question(
        db_session, module_id=module.id, question_type=EXAMPLE_EXERCISE.question_type,
        content_json=content, generation_source="manual",
    )
    assert question.id


@pytest.mark.parametrize(
    "change, message",
    [
        ({"context": "Trop court."}, "Contexte insuffisant"),
        ({"criteria": ()}, "Barème requis"),
        ({"instructions": ("Que signifie l'acronyme UTP ?",)}, "acronyme"),
        ({"title": "Sujet officiel 2026"}, "officiel"),
        ({"requirement_ids": ("AP-99",)}, "Exigence inconnue"),
    ],
)
def test_validation_rejects_forbidden_exercises(change, message):
    errors = validate_exercise(replace(EXAMPLE_EXERCISE, **change))
    assert any(message in e for e in errors), errors
    with pytest.raises(ValueError):
        to_question_content(replace(EXAMPLE_EXERCISE, **change), [1])


# --- Pages ---------------------------------------------------------------------------------


def test_home_shows_modules_slots_as_upcoming_and_day_instructions(client):
    response = client.get("/ampcr-pratique")
    assert response.status_code == 200
    text = _text(response.text)
    assert "0 cours publiés sur 30 prévus" in text
    assert text.count("À venir") == 36
    for i in range(1, 7):
        assert f"Module {i} — " in text
    assert "L’EXAMEN SE FERA UNIQUEMENT PAR ÉCRIT." in text
    assert "/ampcr-pratique/matrice" in response.text


def test_home_links_published_course_and_theory(db_session, client):
    subject = Subject(name="Informatique", slug="informatique")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="AMPCR", slug="ampcr", subject_id=subject.id)
    db_session.add(module)
    db_session.flush()
    practical = Module(code=plan.PRACTICAL_MODULE_CODE, slug="ampcr-pratique", subject_id=subject.id)
    db_session.add(practical)
    db_session.flush()
    db_session.add_all([
        UAA(code="MC05", title="Alimentation", slug="ampcr-mc05", position=5, is_published=True, module_id=module.id),
        # Même code dans un autre module : jamais pris pour un cours pratique.
        UAA(code="PR06", title="Autre", slug="autre-pr06", position=6, is_published=True, module_id=module.id),
        UAA(code="PR04", title="Alimentation PC (pratique)", slug="ampcr-pratique-pr04", position=1, is_published=True, module_id=practical.id),
        UAA(code="PR05", title="Brouillon", slug="ampcr-pratique-pr05", position=2, is_published=False, module_id=practical.id),
    ])
    db_session.commit()
    html = client.get("/ampcr-pratique").text
    assert 'href="/uaa/ampcr-pratique-pr04"' in html
    assert "autre-pr06" not in html
    assert 'href="/uaa/ampcr-mc05"' in html
    assert "ampcr-pratique-pr05" not in html  # non publié : jamais affiché comme disponible
    assert "1 cours publiés sur 30 prévus" in _text(html)
    matrix = _text(client.get("/ampcr-pratique/matrice").text)
    assert "partiel" in matrix
    assert "Couverture non complète." in matrix


def test_matrix_lists_every_requirement(client):
    response = client.get("/ampcr-pratique/matrice")
    assert response.status_code == 200
    for req in plan.ALL_REQUIREMENTS:
        assert f'id="{req.id}"' in response.text
    text = _text(response.text)
    assert "38 exigences officielles — 0 validée(s), 0 partielle(s), 38 non traitée(s)" in text
    assert plan.OFFICIAL_SOURCE.sha256 in text


def test_format_page_printable_and_flagged_non_official(client):
    response = client.get("/ampcr-pratique/format-exercice")
    assert response.status_code == 200
    text = _text(response.text)
    assert "Exemple de format, non officiel." in text
    assert "Barème et correction justifiée" in text
    assert "@page { size: A4" in response.text


def test_dashboard_and_theory_module_link_to_practical_path(db_session, client):
    subject = Subject(name="Informatique", slug="informatique")
    db_session.add(subject)
    db_session.flush()
    db_session.add(Module(code="AMPCR", slug="ampcr", subject_id=subject.id))
    db_session.commit()
    token = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/parcours?diplome=cess&forme=p").text).group(1)
    client.post("/parcours/choisir", data={"csrf_token": token, "diploma": "cess", "form": "p", "option": "ampcr"})
    assert 'href="/ampcr-pratique"' in client.get("/mon-parcours").text
    assert 'href="/ampcr-pratique"' in client.get("/modules/ampcr").text


def test_documentation_matrix_lists_every_requirement():
    from pathlib import Path

    doc = (Path(__file__).resolve().parents[1] / "docs" / "ampcr_pratique_v1.md").read_text()
    for req in plan.ALL_REQUIREMENTS:
        assert f"| {req.id} | {req.text}" in doc, req.id
    assert plan.OFFICIAL_SOURCE.sha256 in doc

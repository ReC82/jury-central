"""Ticket #236 — audit de la numérotation AMPCR pratique écrite (PR01–PR30 / EX01–EX06).

Les 36 tickets GitHub font foi (décision du propriétaire, 26/10/2026) : la correspondance
code → ticket → titre est figée ici, recopiée des titres GitHub. Un changement de plan qui
ne suit pas un ticket fait échouer ces tests. Aucune IA, aucune écriture hors base de test."""

import html
import re
from pathlib import Path

import pytest

from app.v1 import ampcr_pratique_plan as plan
from app.v1 import ampcr_pratique_tickets as tickets
from app.v1.ampcr_plan import AMPCR_PLAN_BY_CODE
from app.v1.ampcr_pratique_bank import PRACTICAL_COURSES

DOCS = Path(__file__).resolve().parents[1] / "docs"

# Titres GitHub au 26/10/2026, sans le préfixe « [Px][AMPCR pratique XXnn] ».
EXPECTED_COURSES: dict[str, tuple[int, str]] = {
    "PR01": (202, "Structure d'un PC et identification des composants"),
    "PR02": (203, "Alimentation, connectique, compatibilité et sécurité"),
    "PR03": (204, "Montage et démontage d'un PC — procédure écrite"),
    "PR04": (205, "Reconditionnement, entretien et contrôles après intervention"),
    "PR05": (206, "Stockage, partitions, formatage et défragmentation"),
    "PR06": (193, "Diagnostic des pannes matérielles"),
    "PR07": (207, "Systèmes d'exploitation, GUI/CLI et prérequis d'installation"),
    "PR08": (208, "Installation complète de Windows — préparation et dépannage"),
    "PR09": (209, "Installation complète de Linux — préparation et dépannage"),
    "PR10": (214, "Comptes, pilotes, paramètres et commandes"),
    "PR11": (194, "Messages d'erreur Windows/Linux — diagnostic et interventions écrites"),
    "PR12": (215, "Dépannage logiciel et restauration du système"),
    "PR13": (216, "Câbles UTP, FTP, STP et coaxial — choix et pose"),
    "PR14": (217, "Débits, distances, atténuation et impédance"),
    "PR15": (197, "Câblage RJ45 T568A/B — fabrication, schémas et tests"),
    "PR16": (198, "Câble coaxial et BNC — impédance, fabrication et diagnostic écrit"),
    "PR17": (218, "Fibre optique — choix, raccordement et diagnostic"),
    "PR18": (219, "Installation physique d'un mini-réseau"),
    "PR19": (220, "Topologies, OSI, TCP/IP, NetBEUI et équipements"),
    "PR20": (199, "IPv4, MAC, masques et passerelles — configuration et diagnostics écrits"),
    "PR21": (221, "Connexion directe de deux PC et mini-réseau"),
    "PR22": (222, "Domaine, groupe de travail, comptes et groupes"),
    "PR23": (223, "Partage de dossiers, imprimantes et permissions"),
    "PR24": (200, "Dépannage réseau et Internet — dossiers d'intervention écrits"),
    "PR25": (224, "Wi-Fi : configuration, couverture, sécurité et diagnostic"),
    "PR26": (225, "Analyser une demande d'intervention technique"),
    "PR27": (226, "Construire et justifier une procédure de diagnostic"),
    "PR28": (227, "Outillage, sécurité et protection des données"),
    "PR29": (228, "Contrôles finaux et rapport professionnel d'intervention"),
    "PR30": (229, "Grand laboratoire écrit — installation et dépannage d'un réseau complet"),
}
EXPECTED_EXAMS: dict[str, tuple[int, str]] = {
    "EX01": (230, "Examen blanc écrit — maintenance et dépannage matériel"),
    "EX02": (231, "Examen blanc écrit — installation et dépannage des systèmes"),
    "EX03": (232, "Examen blanc écrit — câblage RJ45, BNC et fibre"),
    "EX04": (233, "Examen blanc écrit — réseau, configuration et dépannage"),
    "EX05": (201, "Examen blanc global standard — épreuve pratique écrite"),
    "EX06": (234, "Examen blanc global avancé — dossiers complexes"),
}

# Exigence officielle « signature » de chaque cours d'après la matière de son ticket : un
# glissement de numérotation (sujet d'un autre ticket sous ce code) la ferait disparaître.
SIGNATURE_REQUIREMENT: dict[str, str] = {
    "PR01": "AP-01", "PR02": "AP-04", "PR03": "AP-14", "PR04": "AP-14", "PR05": "AP-03",
    "PR06": "AP-15", "PR07": "AP-08", "PR08": "AP-10", "PR09": "AP-10", "PR10": "AP-11",
    "PR11": "AP-09", "PR12": "AP-15", "PR13": "AP-18", "PR14": "AP-19", "PR15": "AP-34",
    "PR16": "AP-35", "PR17": "AP-21", "PR18": "AP-36", "PR19": "AP-29", "PR20": "AP-30",
    "PR21": "AP-28", "PR22": "AP-24", "PR23": "AP-27", "PR24": "AP-32", "PR25": "AP-33",
    "PR26": "AP-C01", "PR27": "AP-C01", "PR28": "AP-C02", "PR29": "AP-C01", "PR30": "AP-38",
}


def _text(page: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page)))


# --- Correspondance figée avec les tickets GitHub ------------------------------------------


def test_course_codes_tickets_and_titles_match_github():
    assert {c.code: (c.ticket, c.title) for c in plan.COURSE_SLOTS} == EXPECTED_COURSES


def test_exam_codes_tickets_and_titles_match_github():
    assert {e.code: (e.ticket, e.title) for e in plan.EXERCISE_SLOTS} == EXPECTED_EXAMS


def test_30_courses_and_6_exams_in_order_with_unique_ids():
    assert [c.code for c in plan.COURSE_SLOTS] == [f"PR{i:02d}" for i in range(1, 31)]
    assert [e.code for e in plan.EXERCISE_SLOTS] == [f"EX{i:02d}" for i in range(1, 7)]
    slots = plan.COURSE_SLOTS + plan.EXERCISE_SLOTS
    assert len({s.ticket for s in slots}) == 36
    assert len({s.title for s in slots}) == 36
    reserved = {plan.SOCLE_TICKET, plan.NUMBERING_AUDIT_TICKET, plan.FINAL_AUDIT_TICKET}
    assert not reserved & {s.ticket for s in slots}
    assert tickets.EXISTING_TICKETS == {s.code: s.ticket for s in slots}


@pytest.mark.parametrize("code", sorted(SIGNATURE_REQUIREMENT))
def test_each_course_keeps_the_requirement_of_its_ticket_subject(code):
    assert SIGNATURE_REQUIREMENT[code] in plan.COURSE_SLOTS_BY_CODE[code].requirement_ids


def test_modules_are_contiguous_and_global_exams_are_ex05_ex06():
    assert [m.course_codes for m in plan.MODULES] == [
        tuple(f"PR{i:02d}" for i in range(a, b + 1))
        for a, b in ((1, 6), (7, 12), (13, 17), (18, 25), (26, 30))
    ]
    assert [m.exercise_codes for m in plan.MODULES] == [
        ("EX01",), ("EX02",), ("EX03",), ("EX04",), ("EX05", "EX06"),
    ]
    assert [e.code for e in plan.EXERCISE_SLOTS if e.is_global] == ["EX05", "EX06"]


# --- Couverture des exigences ---------------------------------------------------------------


def test_every_official_requirement_has_a_course_and_an_exam():
    for requirement in plan.ALL_REQUIREMENTS:
        assert plan.courses_for_requirement(requirement.id), requirement.id
        assert plan.exercises_for_requirement(requirement.id), requirement.id
    assert len(plan.OFFICIAL_REQUIREMENTS) == 38


def test_no_unknown_or_repeated_requirement_in_a_slot():
    for slot in plan.COURSE_SLOTS + plan.EXERCISE_SLOTS:
        assert slot.requirement_ids, slot.code
        assert len(slot.requirement_ids) == len(set(slot.requirement_ids)), slot.code
        assert set(slot.requirement_ids) <= set(plan.REQUIREMENTS_BY_ID), slot.code


def test_every_course_is_evaluated_by_at_least_one_exam():
    evaluated = {r for e in plan.EXERCISE_SLOTS for r in e.requirement_ids}
    for course in plan.COURSE_SLOTS:
        assert set(course.requirement_ids) & evaluated, course.code


def test_module_exams_only_evaluate_requirements_taught_somewhere():
    taught = {r for c in plan.COURSE_SLOTS for r in c.requirement_ids}
    for exam in plan.EXERCISE_SLOTS:
        assert set(exam.requirement_ids) <= taught, exam.code


def test_complements_stay_flagged_and_never_counted_as_official():
    assert [r.id for r in plan.COMPLEMENT_REQUIREMENTS] == ["AP-C01", "AP-C02", "AP-C03"]
    summary = plan.coverage_summary(plan.coverage_rows(frozenset()))
    assert summary["official_total"] == 38
    assert summary["complement_total"] == 3


# --- Séparation Théorie / Pratique écrite et contenu déjà publié ----------------------------


def test_practical_path_stays_separate_from_theory():
    assert plan.PRACTICAL_MODULE_CODE == "AMPCR-PRATIQUE"
    assert plan.PRACTICAL_PATH_URL == "/ampcr-pratique"
    assert not plan.PLANNED_CODES & set(AMPCR_PLAN_BY_CODE)
    for requirement in plan.ALL_REQUIREMENTS:
        assert set(requirement.theory_codes) <= set(AMPCR_PLAN_BY_CODE), requirement.id


def test_published_practical_courses_keep_their_code_and_subject():
    # PR06 (#193) est le seul cours publié : son code, son titre et son slug ne bougent pas.
    assert PRACTICAL_COURSES
    for course in PRACTICAL_COURSES:
        slot = plan.COURSE_SLOTS_BY_CODE[course.code]
        assert course.title == slot.title
        assert course.slug == f"ampcr-pratique-{course.code.lower()}"
    assert plan.COURSE_SLOTS_BY_CODE["PR06"].title == "Diagnostic des pannes matérielles"


# --- Pages et documentation ---------------------------------------------------------------


def test_home_shows_ticket_titles_and_global_exams(client):
    text = _text(client.get(plan.PRACTICAL_PATH_URL).text)
    for code, (_ticket, title) in {**EXPECTED_COURSES, **EXPECTED_EXAMS}.items():
        assert f"{code} — {title}" in text, code
    assert "Les 5 modules" in text
    assert text.count("(tout le parcours)") == 2


def test_matrix_shows_exams_from_tickets(client):
    page = client.get(f"{plan.PRACTICAL_PATH_URL}/matrice").text
    assert "Examens blancs" in page
    assert 'title="Examen blanc global standard — épreuve pratique écrite">EX05' in page
    assert 'id="AP-C03"' in page


def test_documentation_table_matches_plan():
    doc = (DOCS / "ampcr_pratique_v1.md").read_text(encoding="utf-8")
    for slot in plan.COURSE_SLOTS + plan.EXERCISE_SLOTS:
        assert f"{slot.code} — {slot.title} (#{slot.ticket})" in doc, slot.code
    for requirement in plan.ALL_REQUIREMENTS:
        courses = ", ".join(c.code for c in plan.courses_for_requirement(requirement.id))
        exams = ", ".join(e.code for e in plan.exercises_for_requirement(requirement.id))
        assert re.search(
            rf"^\| {re.escape(requirement.id)} \|.*\| {re.escape(courses)} \| {re.escape(exams)} \|",
            doc, re.MULTILINE,
        ), requirement.id
    assert (DOCS / "ampcr_pratique_tickets.md").read_text(encoding="utf-8") == tickets.render_document()

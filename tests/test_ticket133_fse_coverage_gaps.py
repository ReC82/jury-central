"""Ticket #133 — complète 3 lacunes réelles trouvées par un audit de couverture fin
(découpage item par item du cahier des charges des issues #96-#97), restées non détectées
par l'audit plus large du ticket #131 :

1. FSE02 : l'item « lien avec les agents et flux économiques » (Matière obligatoire,
   issue #97) n'était rappelé nulle part dans FSE02 lui-même.
2. FSE03 : seulement 2 « Exemple N » au lieu des 3 exigés par le contrat de rédaction
   (issues #96-#101, répété pour chaque cours).
3. FSE04 : même lacune structurelle.

Vérifié par comptage objectif sur les 16 cours FSE01-16 avant correctif : FSE03 et FSE04
étaient les deux SEULS cours avec 2 exemples au lieu de 3."""

import re

from app.content import render_markdown
from app.v1.fse02_course import fse02_course_sections
from app.v1.fse03_course import fse03_course_sections
from app.v1.fse04_course import fse04_course_sections


def _example_count(course_py_path: str) -> int:
    with open(course_py_path, encoding="utf-8") as handle:
        source = handle.read()
    return len(set(re.findall(r"Exemple \d", source)))


def test_all_16_generic_and_bespoke_courses_have_exactly_three_examples():
    for code in (
        "fse01", "fse02", "fse03", "fse04", "fse05", "fse06", "fse07", "fse08",
        "fse09", "fse10", "fse11", "fse12", "fse13", "fse14", "fse15", "fse16",
    ):
        count = _example_count(f"app/v1/{code}_course.py")
        assert count == 3, f"{code} : {count} exemples distincts trouvés, 3 attendus"


# =============================================================================================
# FSE02 — lien agents/flux économiques
# =============================================================================================


def test_fse02_theory_explains_link_to_economic_agents_and_flows():
    sections = dict(fse02_course_sections())
    html = render_markdown(sections["FSE02 — Théorie : notions et définitions"])
    assert "**" not in html
    lowered = html.lower()
    assert "agent" in lowered
    assert "flux" in lowered
    assert "ménage" in lowered
    for term in ("ménage", "entreprise", "état"):
        assert term.lower() in lowered or term.capitalize() in html


def test_fse02_memo_reinforces_agents_flows_link():
    sections = dict(fse02_course_sections())
    html = render_markdown(sections["FSE02 — Fiche mémo"])
    assert "flux" in html.lower()


# =============================================================================================
# FSE03 — 3e exemple commenté
# =============================================================================================


def test_fse03_has_three_examples_with_decrypt_titles():
    sections = dict(fse03_course_sections())
    html = render_markdown(sections["FSE03 — Exemples commentés"])
    assert "**" not in html
    assert html.count('<h3 class="jc-example-title">') == 3
    assert html.count('<h4 class="jc-decrypt-title">') == 3
    assert "Une publication professionnelle récente" in html
    assert 'id="document-publication-recente"' in html


def test_fse03_third_example_reinforces_real_identity_vs_perceived_image_nuance():
    sections = dict(fse03_course_sections())
    html = render_markdown(sections["FSE03 — Exemples commentés"])
    assert "volontaire" in html.lower()
    assert "récente" in html.lower()
    # La nuance positive (une trace qui NE crée PAS d'écart) doit être explicite.
    assert "ne créent donc pas un écart" in html or "ne crée pas un écart" in html.lower() or "correspond bien" in html


# =============================================================================================
# FSE04 — 3e exemple commenté
# =============================================================================================


def test_fse04_has_three_examples_with_decrypt_titles():
    sections = dict(fse04_course_sections())
    html = render_markdown(sections["FSE04 — Exemples commentés"])
    assert "**" not in html
    assert html.count('<h3 class="jc-example-title">') == 3
    assert html.count('<h4 class="jc-decrypt-title">') == 3
    assert "Message privé d'une autre membre du groupe" in html
    assert 'id="document-frustration"' in html


def test_fse04_third_example_illustrates_frustration_as_worked_example():
    sections = dict(fse04_course_sections())
    html = render_markdown(sections["FSE04 — Exemples commentés"])
    assert "frustration" in html.lower()
    assert "besoin" in html.lower()
    # Nuance : contraste explicite avec le membre D (désaccord public, exemple 1).
    assert "membre D" in html
    assert "publiquement" in html.lower()


# =============================================================================================
# Pages réelles — notions toujours présentes, rien perdu
# =============================================================================================


def test_full_fse02_page_contains_notions(client, db_session):
    from app.seed import seed

    seed()
    response = client.get("/uaa/fse-fse02")
    assert response.status_code == 200
    text = response.text
    for notion in ("offre médiatique", "interactivité", "abonnement", "publicité", "fonds publics", "agents", "flux"):
        assert notion in text
    assert "provisoire" not in text.lower()


def test_full_fse03_page_still_contains_required_exam_notions(client, db_session):
    from app.seed import seed

    seed()
    response = client.get("/uaa/fse-fse03")
    assert response.status_code == 200
    text = response.text
    for notion in ("identité numérique", "trace", "volontaire", "involontaire", "réputation", "appartenance"):
        assert notion in text
    assert "provisoire" not in text.lower()


def test_full_fse04_page_still_contains_required_exam_notions(client, db_session):
    from app.seed import seed

    seed()
    response = client.get("/uaa/fse-fse04")
    assert response.status_code == 200
    text = response.text
    for notion in ("norme", "valeur", "comportement", "influence sociale", "socialisation", "frustration"):
        assert notion in text
    assert "provisoire" not in text.lower()

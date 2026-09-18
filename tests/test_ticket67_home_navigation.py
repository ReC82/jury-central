"""Ticket #67 — UX navigation : accueil par parcours CESS → CESS P → Informatique.

Passe UX pure (aucun changement à génération/correction/banque/rating/admin/paiement) :
- nouvel arbre statique `app.programs` (CESS → filière → matière), sans nouvelle table ;
- nouvelles routes `/cess`, `/cess/{filiere}`, `/cess/{filiere}/{matiere}` ;
- page d'accueil remplacée (tuile CESS) ;
- header : lien global « S'entraîner » supprimé, « Déconnexion » restylée ;
- aucune ancienne route retirée (`/subjects`, `/modules/{slug}`, `/uaa/{slug}/...`
  inchangées, toujours accessibles).
"""

import re

import pytest

from app.seed import seed


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _register(client, email: str = "eleve-ticket67@example.test"):
    token = _csrf(client.get("/register").text)
    response = client.post(
        "/register",
        data={
            "csrf_token": token, "email": email, "password": "Aa1!aaaaaaaa",
            "password_confirm": "Aa1!aaaaaaaa", "display_name": "Test 67",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text


# --- 1. Parcours CESS → CESS P → Informatique → AMPCR --------------------------------------


def test_home_shows_cess_entry_point(client, db_session):
    seed()
    response = client.get("/")
    assert response.status_code == 200
    assert "CESS" in response.text
    assert 'href="/cess"' in response.text
    # L'ancien message d'accueil générique a disparu.
    assert "en cours de construction" not in response.text


def test_cess_index_shows_p_clickable_and_others_as_soon(client, db_session):
    seed()
    response = client.get("/cess")
    assert response.status_code == 200
    assert 'href="/cess/p"' in response.text
    assert "CESS Professionnel" in response.text
    # G/TTR/TQ annoncées mais non cliquables (§ 5 : prévu, pas implémenté).
    for title in ("CESS Général", "CESS Technique de Transition", "CESS Technique de Qualification"):
        assert title in response.text
    assert 'href="/cess/g"' not in response.text
    assert 'href="/cess/ttr"' not in response.text
    assert 'href="/cess/tq"' not in response.text
    assert response.text.count("Bientôt disponible") == 3


def test_cess_p_shows_informatique_clickable_and_others_as_soon(client, db_session):
    seed()
    response = client.get("/cess/p")
    assert response.status_code == 200
    assert 'href="/cess/p/informatique"' in response.text
    assert "Informatique" in response.text
    for title in ("Français", "Mathématiques", "Sciences"):
        assert title in response.text
    assert 'href="/cess/p/francais"' not in response.text
    assert 'href="/cess/p/maths"' not in response.text
    assert 'href="/cess/p/sciences"' not in response.text


def test_informatique_page_links_to_existing_ampcr_engine(client, db_session):
    seed()
    response = client.get("/cess/p/informatique")
    assert response.status_code == 200
    assert "Assistant/Assistante de maintenance PC-réseaux (AMPCR)" in response.text
    assert 'href="/modules/ampcr"' in response.text
    assert 'href="/modules/ampcr/practice"' in response.text
    assert 'href="/modules/ampcr/exam"' in response.text


def test_breadcrumb_cess_to_informatique(client, db_session):
    seed()
    response = client.get("/cess/p/informatique")
    text = response.text
    assert '<a href="/">Accueil</a>' in text
    assert '<a href="/cess">CESS</a>' in text
    assert '<a href="/cess/p">CESS Professionnel</a>' in text
    assert "Informatique</li>" in text


def test_unwired_cess_p_subject_shows_soon_page_not_404(client, db_session):
    seed()
    response = client.get("/cess/p/francais")
    assert response.status_code == 200
    assert "bientôt" in response.text.lower()


def test_unknown_filiere_is_404(client, db_session):
    seed()
    assert client.get("/cess/inexistante").status_code == 404


def test_unknown_subject_under_known_filiere_is_404(client, db_session):
    seed()
    assert client.get("/cess/p/inexistante").status_code == 404


def test_unavailable_filiere_shows_soon_page_not_404(client, db_session):
    seed()
    response = client.get("/cess/g")
    assert response.status_code == 200
    assert "CESS Général" in response.text


# --- 2. Header ------------------------------------------------------------------------------


def test_global_training_link_removed_from_header(client, db_session):
    seed()
    response = client.get("/")
    assert "/practice/equations" not in response.text
    assert ">S'entraîner<" not in response.text and ">S’entraîner<" not in response.text


def test_practice_equations_route_still_works_unlinked(client, db_session):
    """La route elle-même n'est pas supprimée, seulement retirée du header (§ 1)."""
    seed()
    response = client.get("/practice/equations")
    assert response.status_code == 200


def test_header_shows_mes_entrainements_and_logout_when_authenticated(client, db_session):
    seed()
    _register(client)
    response = client.get("/")
    assert 'href="/mes-sessions"' in response.text
    assert "Mes entraînements" in response.text
    assert "Déconnexion" in response.text
    assert 'action="/logout"' in response.text


def test_header_hides_mes_entrainements_and_logout_when_anonymous(client, db_session):
    seed()
    response = client.get("/")
    assert 'href="/mes-sessions"' not in response.text
    assert "Déconnexion" not in response.text
    assert 'href="/login"' in response.text


def test_logout_button_uses_discreet_style_not_primary_button(client, db_session):
    seed()
    _register(client)
    response = client.get("/")
    assert "jc-nav-logout" in response.text
    # Jamais un gros bouton d'action primaire (§ 2 : "ne pas en faire un gros bouton").
    assert 'class="btn btn-sm jc-nav-logout"' in response.text
    assert 'btn btn-primary' not in response.text.split("jc-nav-logout")[0][-200:]


# --- 3. Non-régression anciennes routes ------------------------------------------------------


def test_old_subjects_routes_still_work(client, db_session):
    seed()
    assert client.get("/subjects").status_code == 200
    assert client.get("/subjects/informatique").status_code == 200
    assert client.get("/modules/ampcr").status_code == 200


def test_public_course_pages_still_accessible_without_login(client, db_session):
    seed()
    assert client.get("/uaa/ampcr-mc01").status_code == 200


def test_practice_and_exam_still_require_login(client, db_session):
    seed()
    response = client.get("/uaa/ampcr-mc01/practice", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")
    response = client.get("/uaa/ampcr-mc01/exam", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


def test_ampcr_global_practice_and_exam_still_require_login(client, db_session):
    seed()
    for path in ("/modules/ampcr/practice", "/modules/ampcr/exam"):
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"].startswith("/login")


def test_login_logout_roundtrip_unaffected(client, db_session):
    """Non-régression auth/session (§ 10) : inscription, session active, déconnexion,
    puis routes protégées de nouveau refusées."""
    seed()
    _register(client)
    assert client.get("/mes-sessions").status_code == 200

    response = client.get("/account")
    token = _csrf(response.text)
    response = client.post("/logout", data={"csrf_token": token}, follow_redirects=False)
    assert response.status_code == 303

    response = client.get("/mes-sessions", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


# --- 4. Mobile / structure HTML --------------------------------------------------------------


@pytest.mark.parametrize("path", ["/", "/cess", "/cess/p", "/cess/p/informatique"])
def test_mobile_viewport_meta_present(client, db_session, path):
    seed()
    response = client.get(path)
    assert 'name="viewport" content="width=device-width, initial-scale=1"' in response.text


@pytest.mark.parametrize("path", ["/", "/cess", "/cess/p", "/cess/p/informatique"])
def test_no_fixed_wide_min_width_that_would_overflow_mobile(client, db_session, path):
    """Aucune largeur fixe imposée qui casserait un écran ~400px (§ 6 : mobile-first)."""
    seed()
    response = client.get(path)
    assert "min-width: 3" not in response.text  # ex. un composant imposant >300px
    assert "min-width:3" not in response.text


def test_tile_grid_css_is_responsive_grid_not_fixed_width():
    with open("app/static/css/design-system.css") as f:
        css = f.read()
    assert ".jc-tile-grid" in css
    assert "grid-template-columns: 1fr" in css  # une seule colonne par défaut (mobile)


# --- 5. app.programs (unitaire, pur) ----------------------------------------------------------


def test_programs_only_p_filiere_available():
    from app.programs import CESS_FILIERES

    available = {f.slug for f in CESS_FILIERES if f.available}
    assert available == {"p"}
    assert {f.slug for f in CESS_FILIERES} == {"p", "g", "ttr", "tq"}


def test_programs_only_informatique_subject_available():
    from app.programs import CESS_P_SUBJECTS

    available = {s.slug for s in CESS_P_SUBJECTS if s.available}
    assert available == {"informatique"}
    assert {s.slug for s in CESS_P_SUBJECTS} == {"informatique", "francais", "maths", "sciences"}


def test_get_filiere_and_get_subject_link_helpers():
    from app.programs import get_filiere, get_subject_link

    assert get_filiere("p") is not None
    assert get_filiere("inexistante") is None
    assert get_subject_link("p", "informatique") is not None
    assert get_subject_link("p", "inexistante") is None
    assert get_subject_link("inexistante", "informatique") is None

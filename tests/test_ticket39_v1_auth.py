"""Ticket #39 — Comptes V1 : authentification utilisateur et rôles extensibles.

Couvre les 22 scénarios minimaux demandés par le ticket. Aucun test ne crée
d'utilisateur dans la vraie `jury_central.db` — tout passe par les fixtures pytest
(`client`, `authenticated_client`, `db_session`), sur une base SQLite temporaire isolée
(voir `tests/conftest.py`)."""

import re

from sqlalchemy import create_engine

import app.database as database_module
from app.database import ensure_schema_migrations
from app.models import UAA, BlockSpace, BlockType, LessonBlock, Module, Subject
from app.v1.auth import (
    hash_password,
    normalize_email,
    require_role,
    safe_next_path,
)
from app.v1.models import User, UserPlan, UserRole


def _extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _build_uaa_with_three_spaces(db_session) -> UAA:
    subject = Subject(name="Matière test 39", slug="matiere-test-39")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MOD39", slug="mod39", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(code="U39", title="UAA test 39", slug="uaa-test-39", is_published=True, module=module)
    db_session.add(uaa)
    db_session.flush()
    db_session.add(LessonBlock(
        uaa=uaa, title="Théorie", type=BlockType.MARKDOWN, content="Contenu cours",
        position=1, is_published=True, space=BlockSpace.COURSE,
    ))
    db_session.add(LessonBlock(
        uaa=uaa, title="Exercice", type=BlockType.MARKDOWN, content="Contenu exercice",
        position=2, is_published=True, space=BlockSpace.PRACTICE,
    ))
    db_session.add(LessonBlock(
        uaa=uaa, title="Examen", type=BlockType.MARKDOWN, content="Contenu examen",
        position=3, is_published=True, space=BlockSpace.EXAM,
    ))
    db_session.commit()
    return uaa


def _register(client, *, email="eleve@example.test", password="test-password-1234", display_name=""):
    csrf_token = _extract_csrf_token(client.get("/register").text)
    return client.post(
        "/register",
        data={
            "csrf_token": csrf_token,
            "email": email,
            "password": password,
            "password_confirm": password,
            "display_name": display_name,
        },
        follow_redirects=False,
    )


# --- 1. Inscription réussie -----------------------------------------------------------------


def test_registration_succeeds(client, db_session):
    response = _register(client)
    assert response.status_code == 303

    user = db_session.query(User).filter_by(email="eleve@example.test").one()
    assert user.is_active is True


# --- 2. Mot de passe jamais stocké en clair -------------------------------------------------


def test_password_never_stored_in_plain_text(client, db_session):
    _register(client, password="MonMotDePasseSecret123")
    user = db_session.query(User).filter_by(email="eleve@example.test").one()

    assert user.password_hash != "MonMotDePasseSecret123"
    assert "MonMotDePasseSecret123" not in user.password_hash
    assert user.password_hash.startswith("$argon2id$")


# --- 3. Duplicate email refusé --------------------------------------------------------------


def test_duplicate_email_rejected(client, db_session):
    _register(client)
    response = _register(client, password="autre-mot-de-passe-1234")

    assert response.status_code == 400
    assert "déjà utilisée" in response.text
    assert db_session.query(User).filter_by(email="eleve@example.test").count() == 1


# --- 4. Email normalisé ----------------------------------------------------------------------


def test_email_is_normalized_on_registration_and_login(client, db_session):
    response = _register(client, email="  User@Example.COM  ", password="test-password-1234")
    assert response.status_code == 303

    user = db_session.query(User).filter_by(email="user@example.com").one_or_none()
    assert user is not None

    # Reconnexion avec une casse différente : doit fonctionner (email normalisé comparé).
    # Déconnexion préalable : /login redirige immédiatement si déjà connecté.
    client.cookies.clear()
    csrf_token = _extract_csrf_token(client.get("/login").text)
    login_response = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "email": "USER@EXAMPLE.COM",
            "password": "test-password-1234",
            "next": "/",
        },
        follow_redirects=False,
    )
    assert login_response.status_code == 303


def test_normalize_email_helper():
    assert normalize_email("  User@Example.COM ") == "user@example.com"


# --- 5. Mot de passe incorrect refusé --------------------------------------------------------


def test_wrong_password_rejected(client, db_session):
    _register(client, password="bon-mot-de-passe-1234")

    csrf_token = _extract_csrf_token(client.get("/login").text)
    response = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "email": "eleve@example.test",
            "password": "mauvais-mot-de-passe",
            "next": "/",
        },
    )
    assert response.status_code == 401
    assert "incorrect" in response.text.lower()


# --- 6. Utilisateur inactif refusé -----------------------------------------------------------


def test_inactive_user_rejected(client, db_session):
    user = User(
        email="inactif@example.test",
        role=UserRole.STUDENT,
        plan=UserPlan.FREE,
        is_active=False,
        password_hash=hash_password("un-mot-de-passe-1234"),
    )
    db_session.add(user)
    db_session.commit()

    csrf_token = _extract_csrf_token(client.get("/login").text)
    response = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "email": "inactif@example.test",
            "password": "un-mot-de-passe-1234",
            "next": "/",
        },
    )
    assert response.status_code == 401
    assert "incorrect" in response.text.lower()  # même message générique, voir § 5


# --- 7. Login réussi -------------------------------------------------------------------------


def test_login_succeeds_and_establishes_session(client, db_session):
    _register(client, password="test-password-1234")
    client.cookies.clear()  # simule une nouvelle visite, sans session active

    csrf_token = _extract_csrf_token(client.get("/login").text)
    response = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "email": "eleve@example.test",
            "password": "test-password-1234",
            "next": "/",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    account_response = client.get("/account")
    assert account_response.status_code == 200
    assert "eleve@example.test" in account_response.text


# --- 8. Logout invalide la session ------------------------------------------------------------


def test_logout_invalidates_session(authenticated_client):
    assert authenticated_client.get("/account").status_code == 200

    csrf_token = _extract_csrf_token(authenticated_client.get("/account").text)
    logout_response = authenticated_client.post(
        "/logout", data={"csrf_token": csrf_token}, follow_redirects=False
    )
    assert logout_response.status_code == 303

    account_response = authenticated_client.get("/account", follow_redirects=False)
    assert account_response.status_code == 303
    assert account_response.headers["location"].startswith("/login")


# --- 9. Cookie/session possède les protections prévues ----------------------------------------


def test_session_cookie_has_expected_protections(client):
    response = _register(client)
    set_cookie = response.headers.get("set-cookie", "")
    assert "httponly" in set_cookie.lower()
    assert "samesite=lax" in set_cookie.lower()
    # APP_ENV=local en test (voir tests/conftest.py) : pas de drapeau Secure, cohérent
    # avec un client HTTP local — voir docs/auth_v1.md, § Session, pour le comportement
    # en staging/prod (APP_ENV décide, jamais un choix implicite).
    assert "secure" not in set_cookie.lower()


# --- 10. Open redirect rejeté ------------------------------------------------------------------


def test_open_redirect_rejected_on_login(client, db_session):
    _register(client, password="test-password-1234")
    client.cookies.clear()

    csrf_token = _extract_csrf_token(client.get("/login").text)
    response = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "email": "eleve@example.test",
            "password": "test-password-1234",
            "next": "https://evil.example.com/phishing",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_safe_next_path_rejects_external_and_protocol_relative_urls():
    assert safe_next_path("https://evil.example.com") == "/"
    assert safe_next_path("//evil.example.com") == "/"
    assert safe_next_path("http://evil.example.com") == "/"
    assert safe_next_path("javascript:alert(1)") == "/"
    assert safe_next_path("/uaa/ampcr-mc01/practice") == "/uaa/ampcr-mc01/practice"
    assert safe_next_path(None) == "/"
    assert safe_next_path("") == "/"


# --- 11. CSRF inscription/login/logout ---------------------------------------------------------


def test_csrf_required_for_registration(client):
    response = client.post(
        "/register",
        data={
            "csrf_token": "jeton-invalide",
            "email": "csrf-test@example.test",
            "password": "test-password-1234",
            "password_confirm": "test-password-1234",
            "display_name": "",
        },
    )
    assert response.status_code == 400
    assert "expirée" in response.text.lower() or "réessaie" in response.text.lower()


def test_csrf_required_for_login(client, db_session):
    _register(client, password="test-password-1234")
    client.cookies.clear()

    response = client.post(
        "/login",
        data={
            "csrf_token": "jeton-invalide",
            "email": "eleve@example.test",
            "password": "test-password-1234",
            "next": "/",
        },
    )
    assert response.status_code == 400


def test_csrf_required_for_logout(authenticated_client):
    response = authenticated_client.post(
        "/logout", data={"csrf_token": "jeton-invalide"}, follow_redirects=False
    )
    # La déconnexion échoue silencieusement (redirection identique, session conservée) —
    # voir app.v1.routes.logout_submit : un CSRF invalide ne doit jamais lever d'erreur
    # bruyante sur une simple tentative de déconnexion, mais ne doit pas non plus
    # invalider la session.
    assert response.status_code == 303
    assert authenticated_client.get("/account").status_code == 200


# --- 12./13./14./15. Protection des espaces COURSE/PRACTICE/EXAM -------------------------------


def test_course_accessible_anonymously(client, db_session):
    _build_uaa_with_three_spaces(db_session)
    response = client.get("/uaa/uaa-test-39")
    assert response.status_code == 200
    assert "Théorie" in response.text


def test_practice_inaccessible_anonymously(client, db_session):
    _build_uaa_with_three_spaces(db_session)
    response = client.get("/uaa/uaa-test-39/practice", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")
    assert "next=" in response.headers["location"]


def test_exam_inaccessible_anonymously(client, db_session):
    _build_uaa_with_three_spaces(db_session)
    response = client.get("/uaa/uaa-test-39/exam", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


def test_practice_accessible_when_authenticated(authenticated_client, db_session):
    _build_uaa_with_three_spaces(db_session)
    response = authenticated_client.get("/uaa/uaa-test-39/practice")
    assert response.status_code == 200
    assert "Exercice" in response.text


def test_exam_accessible_when_authenticated(authenticated_client, db_session):
    _build_uaa_with_three_spaces(db_session)
    response = authenticated_client.get("/uaa/uaa-test-39/exam")
    assert response.status_code == 200
    assert "Examen" in response.text


# --- 16. Plusieurs utilisateurs isolés ----------------------------------------------------------


def test_multiple_users_are_isolated(client, db_session):
    _register(client, email="premier@example.test", password="mot-de-passe-1111")
    first_account = client.get("/account").text
    assert "premier@example.test" in first_account

    client.cookies.clear()
    _register(client, email="second@example.test", password="mot-de-passe-2222")
    second_account = client.get("/account").text
    assert "second@example.test" in second_account
    assert "premier@example.test" not in second_account

    assert db_session.query(User).count() == 2


# --- 17./18. Rôle et plan par défaut --------------------------------------------------------


def test_default_role_is_student(client, db_session):
    _register(client)
    user = db_session.query(User).filter_by(email="eleve@example.test").one()
    assert user.role == UserRole.STUDENT


def test_default_plan_is_free(client, db_session):
    _register(client)
    user = db_session.query(User).filter_by(email="eleve@example.test").one()
    assert user.plan == UserPlan.FREE


# --- 19. Helpers de rôle ----------------------------------------------------------------------


def test_require_role_allows_matching_role():
    teacher = User(email="prof@example.test", role=UserRole.TEACHER, plan=UserPlan.FREE)
    dependency = require_role(UserRole.TEACHER, UserRole.ADMIN)
    assert dependency(user=teacher) is teacher


def test_require_role_rejects_non_matching_role():
    from fastapi import HTTPException

    student = User(email="eleve@example.test", role=UserRole.STUDENT, plan=UserPlan.FREE)
    dependency = require_role(UserRole.TEACHER, UserRole.ADMIN)

    try:
        dependency(user=student)
        raise AssertionError("devrait lever HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 403


# --- 20./21. Migration additive sur v1_users déjà existante -------------------------------------


def test_migration_adds_auth_columns_to_pre_existing_v1_users_table(tmp_path, monkeypatch):
    """Simule un staging seedé au ticket #38 (v1_users existe déjà, sans password_hash ni
    last_login_at)."""
    db_path = tmp_path / "pre_v39.db"
    legacy_engine = create_engine(f"sqlite:///{db_path}")
    with legacy_engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE v1_users (
                id INTEGER PRIMARY KEY,
                email VARCHAR(255) UNIQUE,
                display_name VARCHAR(150),
                role VARCHAR(10),
                plan VARCHAR(10),
                is_active BOOLEAN,
                created_at DATETIME,
                updated_at DATETIME
            )
            """
        )
        connection.exec_driver_sql(
            "INSERT INTO v1_users (id, email, role, plan, is_active) "
            "VALUES (1, 'deja-la@example.test', 'STUDENT', 'FREE', 1)"
        )

    monkeypatch.setattr(database_module, "engine", legacy_engine)
    ensure_schema_migrations()

    with legacy_engine.begin() as connection:
        columns = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(v1_users)")}
        assert "password_hash" in columns
        assert "last_login_at" in columns

        row = connection.exec_driver_sql(
            "SELECT email, password_hash FROM v1_users WHERE id = 1"
        ).fetchone()
        assert row[0] == "deja-la@example.test"  # ligne existante intacte
        assert row[1] is None  # nouvelle colonne, nullable, pas de valeur inventée

    legacy_engine.dispose()


def test_migration_second_pass_is_idempotent(tmp_path, monkeypatch):
    db_path = tmp_path / "pre_v39_second.db"
    legacy_engine = create_engine(f"sqlite:///{db_path}")
    with legacy_engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE v1_users (id INTEGER PRIMARY KEY, email VARCHAR(255))"
        )

    monkeypatch.setattr(database_module, "engine", legacy_engine)
    ensure_schema_migrations()
    ensure_schema_migrations()  # ne doit pas lever (colonnes déjà présentes)

    with legacy_engine.begin() as connection:
        columns = [row[1] for row in connection.exec_driver_sql("PRAGMA table_info(v1_users)")]
    assert columns.count("password_hash") == 1
    assert columns.count("last_login_at") == 1

    legacy_engine.dispose()


# --- 22. Admin HTTP Basic existant non régressé -------------------------------------------------


def test_admin_login_still_works_unaffected_by_v1_auth(admin_client):
    response = admin_client.get("/admin/dashboard")
    assert response.status_code == 200


def test_admin_and_v1_sessions_do_not_interfere(client, db_session):
    """Un compte V1 connecté ne doit jamais obtenir l'accès admin, et réciproquement une
    session admin ne doit jamais être vue comme un utilisateur V1 connecté."""
    _register(client, password="test-password-1234")

    admin_response = client.get("/admin/dashboard", follow_redirects=False)
    assert admin_response.status_code == 303
    assert admin_response.headers["location"] == "/admin/login"

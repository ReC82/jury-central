"""Configuration pytest partagée : base de données de test isolée pour les tests TestClient.

Ne touche jamais jury_central.db : DATABASE_URL est fixé sur un fichier SQLite temporaire
avant tout import de app.database / app.main, donc l'engine applicatif entier (y compris
Base.metadata.create_all() exécuté au chargement de app.main) pointe vers ce fichier de test.
Les tests qui ne dépendent pas de client/db_session (générateurs, quiz_import, etc.) ne sont
pas affectés : ils utilisent leurs propres engines indépendants ou ne touchent pas la base.
"""

import os
import re
import tempfile
from pathlib import Path

_TEST_DB_PATH = Path(tempfile.gettempdir()) / "jury_central_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"
os.environ.setdefault("ADMIN_USERNAME", "test-admin")
os.environ.setdefault("ADMIN_PASSWORD", "test-password")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
# Force-cleared (pas setdefault) : sur une machine où /srv/jury-central/.env porte une
# vraie clé (staging), pydantic-settings la lirait sinon directement depuis le fichier dès
# qu'aucune variable d'environnement OPENAI_API_KEY n'est déjà positionnée — un simple
# `setdefault` ne suffit pas à empêcher ce repli. Garantit qu'aucun test ne peut jamais
# déclencher un appel réseau réel vers OpenAI (voir docs/ai_exercise_engine.md, § Tests).
os.environ["OPENAI_API_KEY"] = ""
# Même raison, même mécanisme (ticket #39) : le vrai .env de ce serveur porte
# APP_ENV=staging (réglage légitime pour le déploiement réel), qui active `https_only` sur
# le cookie de session (voir app/main.py, app/config.py::Settings.app_env). `TestClient`
# n'utilise jamais HTTPS : un cookie `Secure` n'y est alors jamais renvoyé par le client
# après le premier `Set-Cookie`, cassant silencieusement toute connexion (admin ET V1) dès
# le second appel. Forcé à "local" pour que la suite de tests ne dépende jamais de ce que
# .env contient sur cette machine.
os.environ["APP_ENV"] = "local"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.main  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402


@pytest.fixture()
def _clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def db_session(_clean_database):
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(_clean_database):
    with TestClient(app.main.app) as test_client:
        yield test_client


@pytest.fixture()
def admin_client(client):
    response = client.post(
        "/admin/login",
        data={
            "username": os.environ["ADMIN_USERNAME"],
            "password": os.environ["ADMIN_PASSWORD"],
        },
    )
    assert response.status_code in (200, 303)
    return client


def _extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable dans le formulaire"
    return match.group(1)


@pytest.fixture()
def authenticated_client(client):
    """Client V1 authentifié (ticket #39) — inscrit puis connecte un compte de test réel
    via les vraies routes `/register`/`/login` (même approche que `admin_client`), pour
    exercer le vrai chemin de code plutôt que d'injecter directement une session. Utilisé
    par tout test qui appelle une route désormais protégée (`/uaa/{slug}/practice`,
    `/uaa/{slug}/exam`, `/practice/api/ai/*`, `/practice/api/editorial/*/verify`)."""
    csrf_token = _extract_csrf_token(client.get("/register").text)
    response = client.post(
        "/register",
        data={
            "csrf_token": csrf_token,
            "email": "eleve-test@example.test",
            "password": "test-password-1234",
            "password_confirm": "test-password-1234",
            "display_name": "Élève Test",
        },
    )
    assert response.status_code in (200, 303)
    return client

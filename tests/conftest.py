"""Configuration pytest partagée : base de données de test isolée pour les tests TestClient.

Ne touche jamais jury_central.db : DATABASE_URL est fixé sur un fichier SQLite temporaire
avant tout import de app.database / app.main, donc l'engine applicatif entier (y compris
Base.metadata.create_all() exécuté au chargement de app.main) pointe vers ce fichier de test.
Les tests qui ne dépendent pas de client/db_session (générateurs, quiz_import, etc.) ne sont
pas affectés : ils utilisent leurs propres engines indépendants ou ne touchent pas la base.
"""

import os
import tempfile
from pathlib import Path

_TEST_DB_PATH = Path(tempfile.gettempdir()) / "jury_central_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"
os.environ.setdefault("ADMIN_USERNAME", "test-admin")
os.environ.setdefault("ADMIN_PASSWORD", "test-password")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

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

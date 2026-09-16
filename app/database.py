import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'jury_central.db'}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema_migrations() -> None:
    """Ajoute les colonnes de schéma manquantes sur une base SQLite déjà existante.

    Le projet n'utilise pas Alembic (voir README.md, docs/development.md) : les nouvelles
    TABLES sont créées par `Base.metadata.create_all` (appelé avant cette fonction, dans
    `app/main.py` et `app/seed.py::seed()`), mais une nouvelle COLONNE sur une table déjà
    existante (staging déjà seedé avant l'ajout de la colonne) doit être ajoutée
    explicitement — `create_all` ne modifie jamais une table existante. Introduit par le
    ticket #22 (`LessonBlock.space`).

    Idempotent (vérifie la présence de la colonne via `PRAGMA table_info` avant de
    l'ajouter) et strictement additif : ne touche jamais aux lignes ni aux colonnes déjà
    présentes, ne supprime rien, aucun `reset-db` requis.
    """
    with engine.begin() as connection:
        table_exists = connection.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='lesson_blocks'"
        ).fetchone()
        if table_exists is None:
            return

        columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(lesson_blocks)").fetchall()
        }
        if "space" not in columns:
            # "COURSE" (nom du membre de l'enum Python, pas sa valeur "course") : c'est ce
            # que SQLAlchemy `Enum(BlockSpace)` écrit par défaut pour les nouvelles lignes
            # (même convention que `BlockType`, déjà observée pour ce projet).
            connection.exec_driver_sql(
                "ALTER TABLE lesson_blocks ADD COLUMN space VARCHAR(10) "
                "NOT NULL DEFAULT 'COURSE'"
            )

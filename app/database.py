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


def _add_column_if_missing(
    connection, *, table: str, column: str, ddl_type: str
) -> None:
    """Ajoute `column` à `table` si absente, sans toucher aux lignes/colonnes déjà
    présentes. Ne s'exécute que si `table` existe déjà (sinon `Base.metadata.create_all`,
    appelé avant cette fonction, l'aura créée avec toutes ses colonnes d'un coup — rien à
    faire ici dans ce cas)."""
    table_exists = connection.exec_driver_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=:table",
        {"table": table},
    ).fetchone()
    if table_exists is None:
        return

    columns = {row[1] for row in connection.exec_driver_sql(f"PRAGMA table_info({table})")}
    if column not in columns:
        connection.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {ddl_type}")


def ensure_schema_migrations() -> None:
    """Ajoute les colonnes de schéma manquantes sur une base SQLite déjà existante.

    Le projet n'utilise pas Alembic (voir README.md, docs/development.md) : les nouvelles
    TABLES sont créées par `Base.metadata.create_all` (appelé avant cette fonction, dans
    `app/main.py` et `app/seed.py::seed()`), mais une nouvelle COLONNE sur une table déjà
    existante (staging déjà seedé avant l'ajout de la colonne) doit être ajoutée
    explicitement — `create_all` ne modifie jamais une table existante. Introduit par le
    ticket #22 (`LessonBlock.space`) ; étendu au ticket #39 (`v1_users.password_hash`/
    `last_login_at`) et au ticket #55 (`v1_questions.uaa_id`) — chaque colonne peut déjà
    exister sur une base seedée avant son introduction.

    Idempotent (vérifie la présence de chaque colonne via `PRAGMA table_info` avant de
    l'ajouter) et strictement additif : ne touche jamais aux lignes ni aux colonnes déjà
    présentes, ne supprime rien, aucun `reset-db` requis.
    """
    with engine.begin() as connection:
        # "COURSE" (nom du membre de l'enum Python, pas sa valeur "course") : c'est ce
        # que SQLAlchemy `Enum(BlockSpace)` écrit par défaut pour les nouvelles lignes
        # (même convention que `BlockType`, déjà observée pour ce projet).
        _add_column_if_missing(
            connection,
            table="lesson_blocks",
            column="space",
            ddl_type="VARCHAR(10) NOT NULL DEFAULT 'COURSE'",
        )
        # Nullable : une ligne v1_users déjà existante (créée avant #39, sans mot de
        # passe) ne peut pas recevoir de valeur par défaut sensée pour un hash — voir
        # `app.v1.models.User`, docstring.
        _add_column_if_missing(
            connection, table="v1_users", column="password_hash", ddl_type="VARCHAR(255)"
        )
        _add_column_if_missing(
            connection, table="v1_users", column="last_login_at", ddl_type="DATETIME"
        )
        # Ticket #55 : v1_questions peut déjà exister depuis #38, créée sans cette colonne
        # — nécessaire pour scoper une question à un mini-cours précis au sein d'un module
        # qui en regroupe plusieurs (ex. AMPCR/MC01..MC38).
        _add_column_if_missing(
            connection, table="v1_questions", column="uaa_id", ddl_type="INTEGER"
        )

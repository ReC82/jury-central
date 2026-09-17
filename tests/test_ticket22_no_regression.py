"""Tests du ticket #22 (« Refonte UX — séparer Cours, Entraînement et Évaluation ») :

- `LessonBlock.space` (COURSE/PRACTICE/EXAM) : défaut rétrocompatible, migration de schéma
  (`ensure_schema_migrations`) sur une base pré-#22 dépourvue de la colonne ;
- les trois routes génériques `/uaa/{slug}`, `/uaa/{slug}/practice`, `/uaa/{slug}/exam`
  filtrent strictement par espace, avec le même comportement 404 que l'ancienne route
  unique ;
- la navigation entre espaces est présente et indique clairement l'espace actif ;
- scénario explicite de reclassification d'un staging déjà seedé AVANT ce ticket (colonne
  `space` tout juste ajoutée, valeur COURSE partout par défaut) — sans `reset-db` ;
- répartition MC01/MC02/MC03 conforme à la décision de ChatGPT, Mathématiques inchangé
  (COURSE par défaut, aucune reclassification nécessaire)."""

import re
import sqlite3
from pathlib import Path

from sqlalchemy import create_engine

import app.database as database_module
from app.database import ensure_schema_migrations
from app.models import UAA, BlockSpace, BlockType, LessonBlock, Module, Subject
from app.seed import (
    INFORMATIQUE_SUBJECT_NAME,
    MC01_BLOCKS,
    MC02_BLOCKS,
    MC03_BLOCKS,
    SUBJECT_NAME,
    seed,
)

# --- Migration de schéma (colonne `space`) --------------------------------------------------


def test_ensure_schema_migrations_adds_space_column_to_legacy_table(tmp_path, monkeypatch):
    """Simule un staging pré-#22 : table `lesson_blocks` existante, sans colonne `space`."""
    db_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TABLE lesson_blocks (
            id INTEGER PRIMARY KEY,
            title VARCHAR(200),
            type VARCHAR(30),
            content TEXT,
            position INTEGER,
            is_published BOOLEAN,
            uaa_id INTEGER
        )
        """
    )
    connection.execute(
        "INSERT INTO lesson_blocks "
        "(title, type, content, position, is_published, uaa_id) "
        "VALUES ('Ancien bloc', 'MARKDOWN', 'contenu', 1, 1, 1)"
    )
    connection.commit()
    connection.close()

    legacy_engine = create_engine(f"sqlite:///{db_path}")
    monkeypatch.setattr(database_module, "engine", legacy_engine)

    ensure_schema_migrations()

    with legacy_engine.begin() as conn:
        columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(lesson_blocks)")}
        assert "space" in columns

        row = conn.exec_driver_sql(
            "SELECT space FROM lesson_blocks WHERE title = 'Ancien bloc'"
        ).fetchone()
        assert row[0] == "COURSE"

    legacy_engine.dispose()


def test_ensure_schema_migrations_is_idempotent(tmp_path, monkeypatch):
    db_path = tmp_path / "legacy2.db"
    connection = sqlite3.connect(db_path)
    connection.execute(
        "CREATE TABLE lesson_blocks (id INTEGER PRIMARY KEY, title VARCHAR(200))"
    )
    connection.commit()
    connection.close()

    legacy_engine = create_engine(f"sqlite:///{db_path}")
    monkeypatch.setattr(database_module, "engine", legacy_engine)

    ensure_schema_migrations()
    ensure_schema_migrations()  # ne doit pas lever (colonne déjà présente)

    with legacy_engine.begin() as conn:
        columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(lesson_blocks)")}
    assert "space" in columns

    legacy_engine.dispose()


def test_ensure_schema_migrations_no_op_when_table_does_not_exist(tmp_path, monkeypatch):
    db_path = tmp_path / "empty.db"
    empty_engine = create_engine(f"sqlite:///{db_path}")
    monkeypatch.setattr(database_module, "engine", empty_engine)

    ensure_schema_migrations()  # ne doit pas lever, table absente

    empty_engine.dispose()


def test_new_lesson_block_defaults_to_course_space(db_session):
    subject = Subject(name="Matière défaut", slug="matiere-defaut-22")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MODDEF", slug="moddef", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(code="UDEF", title="UAA défaut", slug="uaa-defaut", is_published=True, module=module)
    db_session.add(uaa)
    db_session.flush()

    block = LessonBlock(
        uaa=uaa, title="Bloc sans space explicite", type=BlockType.MARKDOWN,
        content="x", position=1, is_published=True,
    )
    db_session.add(block)
    db_session.commit()
    db_session.refresh(block)

    assert block.space == BlockSpace.COURSE


# --- Routes génériques : filtrage par espace ------------------------------------------------


def _build_uaa_with_three_spaces(db_session) -> UAA:
    subject = Subject(name="Matière test 22", slug="matiere-test-22")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MOD22", slug="mod22", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(
        code="U22", title="UAA test 22", slug="uaa-test-22", is_published=True, module=module
    )
    db_session.add(uaa)
    db_session.flush()

    db_session.add(LessonBlock(
        uaa=uaa, title="Théorie X", type=BlockType.MARKDOWN, content="Contenu théorie X",
        position=1, is_published=True, space=BlockSpace.COURSE,
    ))
    db_session.add(LessonBlock(
        uaa=uaa, title="Exercice X", type=BlockType.MARKDOWN, content="Contenu exercice X",
        position=2, is_published=True, space=BlockSpace.PRACTICE,
    ))
    db_session.add(LessonBlock(
        uaa=uaa, title="Examen X", type=BlockType.MARKDOWN, content="Contenu examen X",
        position=3, is_published=True, space=BlockSpace.EXAM,
    ))
    db_session.commit()
    return uaa


def test_course_route_returns_only_course_blocks(client, db_session):
    _build_uaa_with_three_spaces(db_session)
    response = client.get("/uaa/uaa-test-22")
    assert response.status_code == 200
    assert "Théorie X" in response.text
    assert "Exercice X" not in response.text
    assert "Examen X" not in response.text


def test_practice_route_returns_only_practice_blocks(client, db_session):
    _build_uaa_with_three_spaces(db_session)
    response = client.get("/uaa/uaa-test-22/practice")
    assert response.status_code == 200
    assert "Exercice X" in response.text
    assert "Théorie X" not in response.text
    assert "Examen X" not in response.text


def test_exam_route_returns_only_exam_blocks(client, db_session):
    _build_uaa_with_three_spaces(db_session)
    response = client.get("/uaa/uaa-test-22/exam")
    assert response.status_code == 200
    assert "Examen X" in response.text
    assert "Théorie X" not in response.text
    assert "Exercice X" not in response.text


def test_unknown_slug_returns_404_on_all_three_routes(client, db_session):
    for path in ("/uaa/does-not-exist", "/uaa/does-not-exist/practice", "/uaa/does-not-exist/exam"):
        assert client.get(path).status_code == 404


def test_unpublished_uaa_returns_404_on_all_three_routes(client, db_session):
    subject = Subject(name="Matière non publiée", slug="matiere-non-publiee")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MODNP", slug="modnp", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(
        code="UNP", title="UAA non publiée", slug="uaa-non-publiee",
        is_published=False, module=module,
    )
    db_session.add(uaa)
    db_session.commit()

    for path in ("/uaa/uaa-non-publiee", "/uaa/uaa-non-publiee/practice", "/uaa/uaa-non-publiee/exam"):
        assert client.get(path).status_code == 404


# --- Navigation entre espaces -----------------------------------------------------------


def test_space_nav_links_and_active_state(client, db_session):
    _build_uaa_with_three_spaces(db_session)

    course = client.get("/uaa/uaa-test-22").text
    practice = client.get("/uaa/uaa-test-22/practice").text
    exam = client.get("/uaa/uaa-test-22/exam").text

    for page in (course, practice, exam):
        assert "/uaa/uaa-test-22" in page
        assert "/uaa/uaa-test-22/practice" in page
        assert "/uaa/uaa-test-22/exam" in page
        assert "Cours" in page
        assert "S&#39;entraîner" in page or "S'entraîner" in page
        assert "S&#39;évaluer" in page or "S'évaluer" in page

    # Chaque page ne marque actif que son propre onglet DANS le nav d'espace (le
    # breadcrumb porte aussi un `aria-current="page"` distinct, sur son propre élément —
    # on isole donc le bloc `.jc-space-nav` avant de compter).
    def space_nav_html(page: str) -> str:
        match = re.search(r'<nav aria-label="Navigation du module".*?</nav>', page, re.DOTALL)
        assert match is not None
        return match.group(0)

    assert space_nav_html(course).count('aria-current="page"') == 1
    assert space_nav_html(practice).count('aria-current="page"') == 1
    assert space_nav_html(exam).count('aria-current="page"') == 1


def test_space_nav_css_has_adequate_touch_target_size():
    css = Path("app/static/css/design-system.css").read_text(encoding="utf-8")
    assert ".jc-space-nav" in css
    assert "min-height: 44px" in css


# --- Migration du contenu déjà seedé (staging pré-#22) --------------------------------------


def test_staging_seeded_before_ticket_22_is_reclassified_without_reset(client, db_session):
    """Reproduit un staging seedé AVANT le ticket #22 : la colonne `space` vient d'être
    ajoutée par `ensure_schema_migrations` avec sa valeur par défaut COURSE pour TOUTES les
    lignes existantes, y compris les exercices et l'examen. Un seul seed() doit reclasser
    les bons blocs vers PRACTICE/EXAM (métadonnée uniquement), sans toucher au contenu, et
    sans jamais appeler reset()."""
    informatique = Subject(name=INFORMATIQUE_SUBJECT_NAME, slug="informatique")
    db_session.add(informatique)
    db_session.flush()
    ampcr = Module(code="AMPCR", slug="ampcr", subject=informatique)
    db_session.add(ampcr)
    db_session.flush()
    uaa = UAA(
        code="MC01", title="Architecture générale d'un PC", slug="ampcr-mc01",
        position=1, is_published=True, module=ampcr,
    )
    db_session.add(uaa)
    db_session.flush()

    for block_data in MC01_BLOCKS:
        db_session.add(LessonBlock(
            uaa=uaa,
            title=block_data["title"],
            type=block_data["type"],
            content=block_data["content"],
            position=block_data["position"],
            is_published=block_data["is_published"],
            space=BlockSpace.COURSE,  # simule le défaut posé par ensure_schema_migrations
        ))
    db_session.commit()

    seed()
    db_session.expire_all()
    uaa = db_session.query(UAA).filter_by(code="MC01").first()

    by_title = {block.title: block for block in uaa.lesson_blocks}
    for block_data in MC01_BLOCKS:
        expected_space = block_data.get("space", BlockSpace.COURSE)
        actual_block = by_title[block_data["title"]]
        assert actual_block.space == expected_space, block_data["title"]
        # Le contenu n'est jamais touché par la reclassification.
        assert actual_block.content == block_data["content"]

    exam_response = client.get("/uaa/ampcr-mc01/exam")
    assert "Examen final" in exam_response.text
    course_response = client.get("/uaa/ampcr-mc01")
    assert "Examen final" not in course_response.text
    assert "Exercice 1 —" not in course_response.text


def test_seed_second_run_reclassifies_nothing(client, db_session, capsys):
    seed()
    capsys.readouterr()
    seed()
    output = capsys.readouterr().out
    assert "Reclassé" not in output


# --- Répartition COURSE/PRACTICE/EXAM ---------------------------------------------------


def test_mc01_mc02_mc03_block_space_distribution(client, db_session):
    """MC01 : 13 PRACTICE depuis le ticket #29 (12 exercices structurés + 1 bloc IA), tous
    d'anciens blocs Markdown d'exercice ayant été migrés — voir
    tests/test_ticket29_no_regression.py pour la non-régression spécifique à ce ticket."""
    seed()
    expectations = [
        ("MC01", 13, 13, 2),
        ("MC02", 18, 4, 2),
        ("MC03", 19, 4, 2),
    ]
    for code, expected_course, expected_practice, expected_exam in expectations:
        uaa = db_session.query(UAA).filter_by(code=code).first()
        counts = {"course": 0, "practice": 0, "exam": 0}
        for block in uaa.lesson_blocks:
            counts[block.space.value] += 1
        assert counts["course"] == expected_course, code
        assert counts["practice"] == expected_practice, code
        assert counts["exam"] == expected_exam, code


def test_mathematiques_blocks_remain_course_space_by_default(client, db_session):
    """Décision explicite de ChatGPT : Mathématiques reste COURSE par défaut, aucune
    reclassification n'est nécessaire dans ce ticket."""
    seed()
    mathematiques = db_session.query(Subject).filter_by(name=SUBJECT_NAME).first()
    assert mathematiques is not None
    mb32 = next(module for module in mathematiques.modules if module.code == "MB32")
    for uaa in mb32.uaas:
        for block in uaa.lesson_blocks:
            assert block.space == BlockSpace.COURSE, f"{uaa.code}/{block.title}"


def test_mc02_and_mc03_block_dicts_have_no_missing_space_key():
    """Garde-fou anti-régression : chaque entrée de MC02_BLOCKS/MC03_BLOCKS porte bien une
    classification explicite (pas de valeur implicite oubliée par erreur)."""
    for blocks in (MC02_BLOCKS, MC03_BLOCKS):
        for block_data in blocks:
            assert "space" in block_data, block_data["title"]
            assert isinstance(block_data["space"], BlockSpace)

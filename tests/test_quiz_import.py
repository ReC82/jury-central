import csv
import io

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import UAA, BlockType, Module, Subject
from app.quiz import QuizConfig
from app.quiz_import import ALL_COLUMNS, import_quiz_csv


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def sample_uaa(db_session):
    subject = Subject(name="Mathématiques", slug="mathematiques")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MB32", slug="mb32", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(code="UAA1", title="Fonctions du premier degré", slug="mb32-uaa1", module=module)
    db_session.add(uaa)
    db_session.commit()
    return uaa


def _build_csv(rows: list[dict]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=ALL_COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column, "") for column in ALL_COLUMNS})
    return buffer.getvalue()


def _base_row(**overrides) -> dict:
    row = {
        "subject_slug": "mathematiques",
        "module_slug": "mb32",
        "uaa_slug": "mb32-uaa1",
        "title": "Quiz test",
        "question": "Combien font 2 + 2 ?",
        "choice_1": "3",
        "choice_2": "4",
        "choice_3": "",
        "choice_4": "",
        "correct_choice": "2",
        "explanation": "2 + 2 = 4",
        "position": "",
        "is_published": "oui",
    }
    row.update(overrides)
    return row


def test_valid_row_is_imported(db_session, sample_uaa):
    csv_text = _build_csv([_base_row()])
    result = import_quiz_csv(csv_text, db_session)

    assert result.errors == []
    assert len(result.created) == 1

    block = result.created[0]
    assert block.type == BlockType.QUIZ
    assert block.uaa_id == sample_uaa.id
    assert block.is_published is True

    config = QuizConfig.from_json(block.content)
    assert config.question == "Combien font 2 + 2 ?"
    assert config.choices == ["3", "4"]
    assert config.correct_index == 1


def test_missing_required_columns_reports_single_file_level_error(db_session):
    csv_text = "title,question\nx,y\n"
    result = import_quiz_csv(csv_text, db_session)

    assert result.created == []
    assert len(result.errors) == 1
    assert result.errors[0].row_number == 0
    assert "manquantes" in result.errors[0].message


def test_empty_file_reports_error(db_session):
    result = import_quiz_csv("", db_session)

    assert result.created == []
    assert len(result.errors) == 1


def test_unknown_subject_is_rejected(db_session, sample_uaa):
    csv_text = _build_csv([_base_row(subject_slug="inconnu")])
    result = import_quiz_csv(csv_text, db_session)

    assert result.created == []
    assert len(result.errors) == 1
    assert "introuvable" in result.errors[0].message


def test_module_not_belonging_to_subject_is_rejected(db_session, sample_uaa):
    other_subject = Subject(name="Français", slug="francais")
    db_session.add(other_subject)
    db_session.commit()

    csv_text = _build_csv([_base_row(subject_slug="francais")])
    result = import_quiz_csv(csv_text, db_session)

    assert result.created == []
    assert len(result.errors) == 1


def test_uaa_not_belonging_to_module_is_rejected(db_session, sample_uaa):
    other_module = Module(code="MQ32", slug="mq32", subject=sample_uaa.module.subject)
    db_session.add(other_module)
    db_session.commit()

    csv_text = _build_csv([_base_row(module_slug="mq32")])
    result = import_quiz_csv(csv_text, db_session)

    assert result.created == []
    assert len(result.errors) == 1


def test_missing_value_in_required_column_is_rejected(db_session, sample_uaa):
    csv_text = _build_csv([_base_row(question="")])
    result = import_quiz_csv(csv_text, db_session)

    assert result.created == []
    assert len(result.errors) == 1
    assert result.errors[0].row_number == 2


def test_correct_choice_out_of_range_is_rejected(db_session, sample_uaa):
    csv_text = _build_csv([_base_row(correct_choice="9")])
    result = import_quiz_csv(csv_text, db_session)

    assert result.created == []
    assert len(result.errors) == 1


def test_correct_choice_not_a_number_is_rejected(db_session, sample_uaa):
    csv_text = _build_csv([_base_row(correct_choice="B")])
    result = import_quiz_csv(csv_text, db_session)

    assert result.created == []
    assert len(result.errors) == 1


def test_correct_choice_pointing_to_blank_choice_is_rejected(db_session, sample_uaa):
    csv_text = _build_csv([_base_row(choice_3="", correct_choice="3")])
    result = import_quiz_csv(csv_text, db_session)

    assert result.created == []
    assert len(result.errors) == 1


def test_only_one_filled_choice_is_rejected(db_session, sample_uaa):
    csv_text = _build_csv([_base_row(choice_2="", correct_choice="1")])
    result = import_quiz_csv(csv_text, db_session)

    assert result.created == []
    assert len(result.errors) == 1


def test_invalid_position_is_rejected(db_session, sample_uaa):
    csv_text = _build_csv([_base_row(position="pas-un-nombre")])
    result = import_quiz_csv(csv_text, db_session)

    assert result.created == []
    assert len(result.errors) == 1


def test_partial_import_keeps_valid_rows_and_reports_invalid_ones(db_session, sample_uaa):
    csv_text = _build_csv(
        [
            _base_row(title="Quiz valide"),
            _base_row(title="Quiz invalide", uaa_slug="inconnu"),
        ]
    )
    result = import_quiz_csv(csv_text, db_session)

    assert len(result.created) == 1
    assert result.created[0].title == "Quiz valide"
    assert len(result.errors) == 1
    assert result.errors[0].row_number == 3


def test_blank_position_defaults_incrementally(db_session, sample_uaa):
    csv_text = _build_csv(
        [_base_row(title="Quiz A"), _base_row(title="Quiz B")]
    )
    result = import_quiz_csv(csv_text, db_session)

    assert len(result.created) == 2
    positions = {block.title: block.position for block in result.created}
    assert positions["Quiz B"] > positions["Quiz A"]


def test_is_published_defaults_to_false_when_blank(db_session, sample_uaa):
    csv_text = _build_csv([_base_row(is_published="")])
    result = import_quiz_csv(csv_text, db_session)

    assert result.created[0].is_published is False


def test_choices_beyond_two_are_optional(db_session, sample_uaa):
    csv_text = _build_csv(
        [_base_row(choice_3="5", choice_4="6", correct_choice="3")]
    )
    result = import_quiz_csv(csv_text, db_session)

    assert result.errors == []
    config = QuizConfig.from_json(result.created[0].content)
    assert config.choices == ["3", "4", "5", "6"]
    assert config.correct_index == 2

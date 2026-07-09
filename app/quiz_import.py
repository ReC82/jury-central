import csv
import io
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models import UAA, BlockType, LessonBlock, Module, Subject
from app.quiz import build_quiz_config

REQUIRED_COLUMNS = [
    "subject_slug",
    "module_slug",
    "uaa_slug",
    "title",
    "question",
    "choice_1",
    "choice_2",
    "correct_choice",
]

OPTIONAL_COLUMNS = ["choice_3", "choice_4", "explanation", "position", "is_published"]

ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS

_TRUE_VALUES = {"1", "true", "vrai", "oui", "yes", "y"}


@dataclass
class ImportRowError:
    row_number: int
    message: str


@dataclass
class ImportResult:
    created: list[LessonBlock] = field(default_factory=list)
    errors: list[ImportRowError] = field(default_factory=list)


def _parse_position(raw: str, default: int) -> tuple[int | None, str | None]:
    raw = (raw or "").strip()
    if not raw:
        return default, None
    try:
        return int(raw), None
    except ValueError:
        return None, "« position » doit être un nombre entier."


def _parse_is_published(raw: str) -> bool:
    return (raw or "").strip().lower() in _TRUE_VALUES


def import_quiz_csv(csv_text: str, db: Session) -> ImportResult:
    reader = csv.DictReader(io.StringIO(csv_text))

    if not reader.fieldnames:
        return ImportResult(errors=[ImportRowError(0, "Fichier CSV vide ou illisible.")])

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
    if missing_columns:
        message = "Colonnes obligatoires manquantes : " + ", ".join(missing_columns)
        return ImportResult(errors=[ImportRowError(0, message)])

    errors: list[ImportRowError] = []
    to_create: list[dict] = []
    next_position_by_uaa: dict[int, int] = {}

    for row_number, row in enumerate(reader, start=2):
        missing_values = [c for c in REQUIRED_COLUMNS if not (row.get(c) or "").strip()]
        if missing_values:
            errors.append(
                ImportRowError(
                    row_number, "Colonne(s) vide(s) : " + ", ".join(missing_values)
                )
            )
            continue

        subject = db.query(Subject).filter_by(slug=row["subject_slug"].strip()).first()
        if subject is None:
            errors.append(
                ImportRowError(row_number, f"Matière « {row['subject_slug']} » introuvable.")
            )
            continue

        module = db.query(Module).filter_by(slug=row["module_slug"].strip()).first()
        if module is None or module.subject_id != subject.id:
            errors.append(
                ImportRowError(
                    row_number,
                    f"Module « {row['module_slug']} » introuvable dans la matière "
                    f"« {row['subject_slug']} ».",
                )
            )
            continue

        uaa = db.query(UAA).filter_by(slug=row["uaa_slug"].strip()).first()
        if uaa is None or uaa.module_id != module.id:
            errors.append(
                ImportRowError(
                    row_number,
                    f"UAA « {row['uaa_slug']} » introuvable dans le module "
                    f"« {row['module_slug']} ».",
                )
            )
            continue

        try:
            correct_raw_index = int(row["correct_choice"].strip()) - 1
        except ValueError:
            errors.append(
                ImportRowError(row_number, "« correct_choice » doit être un nombre entre 1 et 4.")
            )
            continue

        choices = [row.get(f"choice_{i}", "") or "" for i in range(1, 5)]
        config, error = build_quiz_config(
            question=row["question"],
            choices=choices,
            correct_raw_index=correct_raw_index,
            explanation=row.get("explanation", "") or "",
        )
        if error:
            errors.append(ImportRowError(row_number, error))
            continue

        if uaa.id not in next_position_by_uaa:
            next_position_by_uaa[uaa.id] = (
                max((block.position for block in uaa.lesson_blocks), default=0) + 1
            )
        default_position = next_position_by_uaa[uaa.id]

        position, position_error = _parse_position(row.get("position", ""), default_position)
        if position_error:
            errors.append(ImportRowError(row_number, position_error))
            continue
        next_position_by_uaa[uaa.id] = default_position + 1

        to_create.append(
            {
                "uaa": uaa,
                "title": row["title"].strip(),
                "type": BlockType.QUIZ,
                "content": config.to_json(),
                "position": position,
                "is_published": _parse_is_published(row.get("is_published", "")),
            }
        )

    created = [LessonBlock(**kwargs) for kwargs in to_create]
    if created:
        db.add_all(created)
        db.commit()

    return ImportResult(created=created, errors=errors)

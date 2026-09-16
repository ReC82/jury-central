import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BlockType(str, enum.Enum):
    MARKDOWN = "markdown"
    YOUTUBE = "youtube"
    IMAGE = "image"
    PDF = "pdf"
    EXERCISE = "exercise"
    QUIZ = "quiz"
    GENERATED_EXERCISE = "generated_exercise"
    AI_EXERCISE = "ai_exercise"
    EDITORIAL_EXERCISE = "editorial_exercise"


class BlockSpace(str, enum.Enum):
    """Espace pédagogique dans lequel un bloc est affiché (ticket #22) : COURS, S'ENTRAÎNER
    ou S'ÉVALUER. Champ EXPLICITE, indépendant de `BlockType` (nature technique du bloc) —
    un bloc `editorial_exercise` peut par exemple appartenir à PRACTICE aujourd'hui et à
    EXAM demain, sans changer de type. Ne jamais déduire `space` du titre, de la position
    ou du type à l'exécution (voir `app/main.py`, routes `/uaa/{slug}`,
    `/uaa/{slug}/practice`, `/uaa/{slug}/exam`) : seule la valeur explicite en base fait foi.
    """

    COURSE = "course"
    PRACTICE = "practice"
    EXAM = "exam"


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    modules: Mapped[list["Module"]] = relationship(
        back_populates="subject", cascade="all, delete-orphan"
    )


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20))
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))

    subject: Mapped["Subject"] = relationship(back_populates="modules")
    uaas: Mapped[list["UAA"]] = relationship(
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="UAA.position",
    )


class UAA(Base):
    __tablename__ = "uaas"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))

    module: Mapped["Module"] = relationship(back_populates="uaas")
    lesson_blocks: Mapped[list["LessonBlock"]] = relationship(
        back_populates="uaa",
        cascade="all, delete-orphan",
        order_by="LessonBlock.position",
    )


class LessonBlock(Base):
    __tablename__ = "lesson_blocks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    type: Mapped[BlockType] = mapped_column(Enum(BlockType))
    content: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    # Rétrocompatible : tout bloc existant avant le ticket #22 (colonne ajoutée via
    # `app.database.ensure_schema_migrations`, voir ce module) vaut COURSE par défaut.
    space: Mapped[BlockSpace] = mapped_column(
        Enum(BlockSpace), default=BlockSpace.COURSE, server_default="COURSE"
    )
    uaa_id: Mapped[int] = mapped_column(ForeignKey("uaas.id"))

    uaa: Mapped["UAA"] = relationship(back_populates="lesson_blocks")

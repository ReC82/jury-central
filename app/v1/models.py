"""Socle de données persistant de l'architecture V1 (ticket #38).

Contexte : la V1 introduit un compte utilisateur, une banque locale de questions
réutilisables (versionnées), des sessions de questionnaire persistantes et reprenables,
et un historique complet par utilisateur — pour toutes les matières, en commençant par
Informatique AMPCR et Français CESS Professionnel (voir le ticket GitHub #38).

Ce module pose UNIQUEMENT le modèle de données. Il ne construit ni l'authentification
complète (#39), ni les schémas détaillés par type de question (#40), ni la sélection
depuis la banque (#41), ni l'API d'autosave (#42), ni la génération (#43), ni la
correction (#44), ni l'algorithme de rating (#45), ni l'admin V1 (#46), ni l'UI Français
(#47), ni la reconnaissance d'image (#48).

Réutilisation du socle existant (audit préalable, voir
`docs/claude-reports/2026-09-17_ticket-38_v1-persistent-model.md`, § Audit) :
- `Question.module_id` référence `app.models.Module` (Subject → Module → UAA →
  LessonBlock déjà existant) plutôt que de dupliquer une hiérarchie matière/module — voir
  la discussion du choix de granularité dans `docs/architecture_v1_data_model.md`.
- Le vocabulaire des types de question (`QuestionVersion.question_type`) reste celui déjà
  défini par le contrat questionnaire du ticket #23 (`app.ai.schemas.QUESTION_TYPES`) —
  aucun second vocabulaire de types n'est créé ici. Stocké en texte libre (pas un
  `Enum` SQL) pour ne pas figer le schéma avant le ticket #40.
- Les enums `Role`/`Plan` ne sont PAS des tables séparées : suit la convention déjà
  établie par `app.models.BlockType`/`BlockSpace` (enum Python + colonne
  `Enum(...)` SQLAlchemy) plutôt que d'introduire un mécanisme de lookup-table inédit
  dans ce projet — voir « points ambigus » dans le rapport de ticket.

Immutabilité / pas de suppression physique (principe transversal à tout ce module) :
aucune route, aucun helper de ce module ne supprime jamais une ligne de `Question`,
`QuestionVersion`, `SourceDocument`, `SourceDocumentVersion`, `Asset`, `User` ou
`QuestionnaireSession` une fois créée — un contenu devenu invalide change de `status`
(ARCHIVED/OBSOLETE/INVALID), il n'est jamais retiré de la base. Voir
`docs/architecture_v1_data_model.md`, § Règles d'immutabilité, pour le détail par table.
"""

import enum
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship, validates

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


# =========================================================================================
# A. Utilisateurs / rôles / plans
# =========================================================================================


class UserRole(str, enum.Enum):
    """Rôle applicatif V1. L'authentification (mot de passe, sessions de connexion,
    inscription) arrive au ticket #39 — ce champ existe déjà pour que les entités qui en
    dépendent (sessions, historique, rating) puissent être modélisées dès maintenant."""

    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    AUTHOR = "author"


class UserPlan(str, enum.Enum):
    """Plan d'abonnement V1. Le paiement réel n'est pas dans ce ticket (voir § M,
    `AIUsage`, pour le suivi de quota associé) — seule la valeur du plan est modélisée."""

    FREE = "free"
    PREMIUM = "premium"
    # Compte interne (équipe pédagogique/technique) : pas de quota commercial applicable.
    INTERNAL = "internal"


class User(Base):
    """Un compte = un utilisateur V1 (voir docstring du module). Les champs
    d'authentification (mot de passe, jetons de session) sont volontairement absents :
    ticket #39."""

    __tablename__ = "v1_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT)
    plan: Mapped[UserPlan] = mapped_column(Enum(UserPlan), default=UserPlan.FREE)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


# =========================================================================================
# Statut partagé Question / Asset (voir docstring du module — même concept, jamais
# dupliqué entre les deux tables qui en ont besoin).
# =========================================================================================


class ContentStatus(str, enum.Enum):
    """Statut de cycle de vie d'un contenu versionné (Question ou Asset). Jamais de
    suppression physique associée à un changement de statut — voir docstring du module."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    FLAGGED = "flagged"
    INVALID = "invalid"
    OBSOLETE = "obsolete"
    REVIEW_NEEDED = "review_needed"


class GenerationSource(str, enum.Enum):
    """D'où vient le contenu initial d'une Question. `IMPORTED` anticipe une éventuelle
    reprise future du contenu déjà éditorialisé (`app.editorial_exercise`/`app.quiz`) dans
    la banque V1 — aucune migration de ce type n'est faite par ce ticket."""

    AI_GENERATED = "ai_generated"
    MANUAL = "manual"
    IMPORTED = "imported"


class QuestionDifficulty(str, enum.Enum):
    """Difficulté déclarée à l'auteurisation/génération — jamais recalculée
    automatiquement (voir `Question.difficulty_rating` pour la difficulté empirique,
    distincte par principe, voir § K du ticket)."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# =========================================================================================
# B. / C. Question et QuestionVersion
# =========================================================================================


class Question(Base):
    """Identité logique permanente d'une question (§ B du ticket #38).

    Ne porte aucun contenu directement : le contenu vit exclusivement dans
    `QuestionVersion` (§ C) — modifier une question crée toujours une nouvelle version,
    jamais une modification en place de la version courante (voir
    `create_question`/`add_question_version` ci-dessous, les seuls points d'entrée prévus
    pour créer une Question ou lui ajouter une version)."""

    __tablename__ = "v1_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), index=True)
    # Nullable uniquement le temps très court, à la création, entre l'insertion de la
    # Question et celle de sa première QuestionVersion (référence circulaire) — voir
    # `create_question`. Une Question complètement créée a toujours une current_version.
    # `use_alter=True` : signale à SQLAlchemy que ce cycle Question<->QuestionVersion peut
    # être résolu par un ALTER différé (jamais réellement émis par `create_all`/`drop_all`
    # sur SQLite, qui n'a pas besoin d'ordonner les créations grâce à `checkfirst`) —
    # supprime l'avertissement « unresolvable foreign key dependency » sur `drop_all`
    # (utilisé par `tests/conftest.py` avant chaque test) et reste portable vers
    # PostgreSQL, où un ALTER différé est réellement possible.
    current_version_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "v1_question_versions.id", use_alter=True, name="fk_v1_questions_current_version_id"
        ),
        nullable=True,
    )
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus), default=ContentStatus.ACTIVE, index=True
    )
    difficulty_declared: Mapped[QuestionDifficulty | None] = mapped_column(
        Enum(QuestionDifficulty), nullable=True
    )
    # Difficulté empirique (§ K) : calculée plus tard par l'algorithme du ticket #45.
    # Valeur/contraintes seulement ici — aucun calcul.
    difficulty_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    rating_sample_size: Mapped[int] = mapped_column(Integer, default=0)
    generation_source: Mapped[GenerationSource] = mapped_column(Enum(GenerationSource))
    # Statistiques de base (§ B) : évitent de ré-agréger SessionAnswer à chaque affichage
    # de la banque. Mises à jour par les tickets consommateurs (#41/#44), pas ici.
    times_served: Mapped[int] = mapped_column(Integer, default=0)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    module = relationship("Module")
    versions: Mapped[list["QuestionVersion"]] = relationship(
        back_populates="question",
        foreign_keys="QuestionVersion.question_id",
        order_by="QuestionVersion.version",
        # Jamais de cascade delete : archiver/supprimer une Question ne doit jamais
        # entraîner la suppression de ses versions historiques (voir § Intégrité du
        # ticket : « question archivée conserve toutes ses versions »).
    )
    # `post_update=True` : rompt la dépendance circulaire Question ↔ QuestionVersion au
    # flush (voir SQLAlchemy, « Rows that point to themselves / Mutually Dependent Rows »)
    # — la Question est insérée avec current_version_id NULL, puis la version, puis un
    # UPDATE fixe current_version_id. `create_question` ci-dessous fait cela explicitement
    # via flush() plutôt que de compter uniquement sur ce mécanisme implicite.
    current_version: Mapped["QuestionVersion | None"] = relationship(
        foreign_keys=[current_version_id], post_update=True
    )
    concepts: Mapped[list["Concept"]] = relationship(
        secondary="v1_question_concepts", back_populates="questions"
    )

    __table_args__ = (Index("ix_v1_questions_module_status", "module_id", "status"),)


class QuestionVersion(Base):
    """Contenu concret et immuable d'une Question à un instant donné (§ C).

    Une fois créée, une ligne de cette table n'est plus jamais modifiée (pas d'UPDATE de
    `content_json` ni d'aucun autre champ après création) : une édition crée toujours une
    nouvelle ligne avec `version` incrémenté. C'est cette immutabilité qui garantit
    qu'une session historique (`SessionQuestion.question_version_id`) reste exacte pour
    toujours, même si la Question a depuis une version plus récente."""

    __tablename__ = "v1_question_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("v1_questions.id"), index=True
    )
    version: Mapped[int] = mapped_column(Integer)
    # Vocabulaire des types : `app.ai.schemas.QUESTION_TYPES` (ticket #23), réutilisé tel
    # quel — voir docstring du module. Texte libre (pas un `Enum` SQL) : le schéma complet
    # par type appartient au ticket #40 et ne doit pas nécessiter de migration ici.
    question_type: Mapped[str] = mapped_column(String(50), index=True)
    schema_version: Mapped[int] = mapped_column(Integer, default=1)
    # Contenu générique versionné (§ C) : forme conceptuelle alignée sur
    # `app.ai.schemas.QuestionnaireQuestion` pour schema_version=1 (prompt, options,
    # réponse(s) correcte(s), etc.) — aucun schéma strict imposé au niveau base, validé
    # au niveau applicatif par le ticket #40.
    content_json: Mapped[dict | list] = mapped_column(JSON)
    generator_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_program_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Optionnel (§ E) : ancre une QuestionVersion à la version exacte d'un document source
    # partagé (compréhension à la lecture, Français) — jamais à un SourceDocument
    # « vivant », toujours à une SourceDocumentVersion immuable précise.
    source_document_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("v1_source_document_versions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    question: Mapped["Question"] = relationship(
        back_populates="versions", foreign_keys=[question_id]
    )
    source_document_version: Mapped["SourceDocumentVersion | None"] = relationship()

    __table_args__ = (
        UniqueConstraint("question_id", "version", name="uq_v1_question_versions_question_version"),
    )

    @validates("version")
    def _validate_version(self, _key: str, value: int) -> int:
        if value < 1:
            raise ValueError("QuestionVersion.version doit être >= 1.")
        return value


# =========================================================================================
# D. Concepts / tags
# =========================================================================================


class Concept(Base):
    """Notion/compétence transversale (§ D) — jamais spécialisée par matière : une même
    table sert Informatique (« RAM », « CPU »), Français (« argumentation », « résumé »),
    et toute matière future."""

    __tablename__ = "v1_concepts"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(150))

    questions: Mapped[list["Question"]] = relationship(
        secondary="v1_question_concepts", back_populates="concepts"
    )


class QuestionConcept(Base):
    """Association Question ↔ Concept (plusieurs concepts par question, § D). Liée à la
    Question (identité), pas à une QuestionVersion précise : un tag de compétence reste
    valable à travers les révisions de contenu d'une même question."""

    __tablename__ = "v1_question_concepts"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("v1_questions.id"), index=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("v1_concepts.id"), index=True)

    __table_args__ = (
        UniqueConstraint("question_id", "concept_id", name="uq_v1_question_concepts"),
    )


# =========================================================================================
# E. Source documents (Français — compréhension à la lecture)
# =========================================================================================


class SourceDocument(Base):
    """Identité permanente d'un document source partagé entre plusieurs questions (§ E).
    Même principe d'immutabilité que Question/QuestionVersion : le contenu réel vit dans
    `SourceDocumentVersion`, jamais ici."""

    __tablename__ = "v1_source_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int | None] = mapped_column(
        ForeignKey("modules.id"), nullable=True, index=True
    )
    # Même raison et même mécanisme (`use_alter=True`) que `Question.current_version_id`.
    current_version_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "v1_source_document_versions.id",
            use_alter=True,
            name="fk_v1_source_documents_current_version_id",
        ),
        nullable=True,
    )
    status: Mapped[ContentStatus] = mapped_column(Enum(ContentStatus), default=ContentStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    versions: Mapped[list["SourceDocumentVersion"]] = relationship(
        back_populates="source_document",
        foreign_keys="SourceDocumentVersion.source_document_id",
        order_by="SourceDocumentVersion.version",
    )
    current_version: Mapped["SourceDocumentVersion | None"] = relationship(
        foreign_keys=[current_version_id], post_update=True
    )


class SourceDocumentVersion(Base):
    """Contenu immuable d'un SourceDocument à un instant donné (§ E). Plusieurs
    QuestionVersion (potentiellement de plusieurs Question différentes) peuvent référencer
    la même ligne — jamais modifiée après création, garantissant qu'un snapshot de session
    (`SessionQuestion.source_document_version_id`) reste exact indéfiniment."""

    __tablename__ = "v1_source_document_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_document_id: Mapped[int] = mapped_column(
        ForeignKey("v1_source_documents.id"), index=True
    )
    version: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Texte long aujourd'hui ; `asset_id` permet plus tard un document non textuel (scan,
    # PDF) sans nouvelle table — voir § F.
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("v1_assets.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    source_document: Mapped["SourceDocument"] = relationship(
        back_populates="versions", foreign_keys=[source_document_id]
    )
    asset: Mapped["Asset | None"] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "source_document_id", "version", name="uq_v1_source_document_versions"
        ),
    )

    @validates("version")
    def _validate_version(self, _key: str, value: int) -> int:
        if value < 1:
            raise ValueError("SourceDocumentVersion.version doit être >= 1.")
        return value


# =========================================================================================
# F. Assets
# =========================================================================================


class AssetKind(str, enum.Enum):
    IMAGE = "image"
    SVG = "svg"
    CHART = "chart"
    FORMULA = "formula"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"


class AssetSourceType(str, enum.Enum):
    MANUAL = "manual"
    AI_GENERATED = "ai_generated"
    OFFICIAL = "official"
    EXTERNAL = "external"


class Asset(Base):
    """Ressource réutilisable par plusieurs questions (§ F) : image, SVG, graphique,
    formule, document, et plus tard audio/vidéo. Jamais supprimée physiquement ni
    modifiée en place — un remplacement crée un nouvel Asset, l'ancien reste `ARCHIVED`
    tant qu'une QuestionVersion ou SourceDocumentVersion le référence encore (voir §
    Intégrité : « assets partagés ne sont pas supprimés en cascade par une question »)."""

    __tablename__ = "v1_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[AssetKind] = mapped_column(Enum(AssetKind), index=True)
    # Chemin/clé de stockage local (ex. app/static/...) — nullable si la ressource n'est
    # référencée que par `source_url` (source_type=EXTERNAL).
    storage_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_type: Mapped[AssetSourceType] = mapped_column(Enum(AssetSourceType))
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    license: Mapped[str | None] = mapped_column(String(200), nullable=True)
    provenance: Mapped[str | None] = mapped_column(String(300), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[ContentStatus] = mapped_column(Enum(ContentStatus), default=ContentStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    @validates("storage_ref", "source_url")
    def _validate_reference(self, key: str, value: str | None) -> str | None:
        # Ne peut se prononcer définitivement qu'après les deux affectations ; les tests
        # couvrent l'invariant applicatif (voir test_asset_requires_a_reference), cette
        # validation reste une aide au niveau attribut plutôt qu'une contrainte SQL stricte
        # (SQLite CHECK inter-colonnes serait plus rigide qu'utile avant le ticket #48).
        return value


class QuestionAsset(Base):
    """Association Asset ↔ QuestionVersion (§ F). Scopée à la VERSION plutôt qu'à la
    Question (déviation mineure du nom littéral du ticket, documentée dans le rapport) :
    un asset utilisé par une question peut changer d'une version à l'autre (ex. schéma
    remplacé lors d'une correction éditoriale) — le lier à la Question rétroactivement
    changerait silencieusement ce qu'une ancienne session affiche en relecture, ce que le
    ticket interdit explicitement (« aucune modification rétroactive des sessions
    historiques »). `role` distingue plusieurs usages du même asset pour une même version
    (ex. « main », « diagram », « thumbnail »)."""

    __tablename__ = "v1_question_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_version_id: Mapped[int] = mapped_column(
        ForeignKey("v1_question_versions.id"), index=True
    )
    asset_id: Mapped[int] = mapped_column(ForeignKey("v1_assets.id"), index=True)
    role: Mapped[str] = mapped_column(String(50), default="main")

    __table_args__ = (
        UniqueConstraint(
            "question_version_id", "asset_id", "role", name="uq_v1_question_assets"
        ),
    )


# =========================================================================================
# G. / H. Sessions et questions de session
# =========================================================================================


class SessionMode(str, enum.Enum):
    """Distinct de `app.models.BlockSpace` malgré le chevauchement lexical PRACTICE/EXAM :
    `BlockSpace` classe un bloc de COURS existant (où l'afficher), `SessionMode` classe un
    questionnaire V1 (ce qu'il évalue) — deux concepts différents, pas de réutilisation
    forcée entre le socle éditorial existant et le socle V1."""

    PRACTICE = "practice"
    EXAM = "exam"


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SessionDifficultyRequest(str, enum.Enum):
    """Difficulté demandée pour la SÉLECTION des questions d'une session — distincte de
    `QuestionDifficulty` (déclarée par question) : `ADAPTIVE` n'a de sens qu'au niveau
    d'une stratégie de sélection, jamais comme propriété d'une question individuelle."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    ADAPTIVE = "adaptive"


class QuestionnaireSession(Base):
    """Session de questionnaire persistante et reprenable (§ G). `question_count` est un
    champ simple (pas de nombre de questions codé en dur) : la règle produit V1 de 10
    questions par questionnaire (voir ticket) est appliquée par l'appelant (#41/#42), pas
    imposée ici."""

    __tablename__ = "v1_questionnaire_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("v1_users.id"), index=True)
    mode: Mapped[SessionMode] = mapped_column(Enum(SessionMode))
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), index=True)
    difficulty_requested: Mapped[SessionDifficultyRequest] = mapped_column(
        Enum(SessionDifficultyRequest)
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.IN_PROGRESS, index=True
    )
    question_count: Mapped[int] = mapped_column(Integer, default=10)
    parameters_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User")
    module = relationship("Module")
    # Une SessionQuestion/SessionAnswer n'a aucun sens hors de sa session : cascade
    # appropriée ici (contrairement à Question/Asset/SourceDocument, jamais en cascade) —
    # même principe que UAA -> LessonBlock déjà établi dans app/models.py. Aucune route de
    # suppression de session n'est construite par ce ticket : ce cascade reste une
    # plomberie ORM défensive, jamais exercée en pratique pour l'instant.
    session_questions: Mapped[list["SessionQuestion"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionQuestion.position",
    )

    __table_args__ = (Index("ix_v1_sessions_user_status", "user_id", "status"),)

    def is_locked(self) -> bool:
        """Une session COMPLETED ou ABANDONED est immuable (§ G : « immutabilité après
        COMPLETED »). L'application effective de cette règle (refuser une écriture) est du
        ressort du service d'autosave (#42) — ce helper expose juste la condition pour
        qu'il n'ait pas à la redéfinir."""
        return self.status != SessionStatus.IN_PROGRESS


class SessionQuestion(Base):
    """Ce qui a été exactement servi à l'utilisateur pour une position donnée d'une
    session (§ H) — le point crucial du modèle V1 : référence une QuestionVersion PRÉCISE
    (jamais juste une Question), garantissant qu'une reprise ultérieure affiche
    exactement le même énoncé même si la Question a depuis une nouvelle version."""

    __tablename__ = "v1_session_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("v1_questionnaire_sessions.id"), index=True
    )
    question_version_id: Mapped[int] = mapped_column(
        ForeignKey("v1_question_versions.id"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    source_document_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("v1_source_document_versions.id"), nullable=True
    )
    # Snapshot dénormalisé optionnel (§ H : « snapshot/options affichées si nécessaire »).
    # La source de vérité reste `question_version_id` (déjà immuable par construction) —
    # ce champ est une défense supplémentaire/cache, jamais requis pour la relecture.
    content_snapshot_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    asset_snapshot_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    points_max: Mapped[float] = mapped_column(Float)

    session: Mapped["QuestionnaireSession"] = relationship(back_populates="session_questions")
    question_version = relationship("QuestionVersion")
    source_document_version: Mapped["SourceDocumentVersion | None"] = relationship()
    answer: Mapped["SessionAnswer | None"] = relationship(
        back_populates="session_question",
        cascade="all, delete-orphan",
        uselist=False,
    )

    __table_args__ = (
        UniqueConstraint("session_id", "position", name="uq_v1_session_questions_position"),
    )

    @validates("points_max")
    def _validate_points_max(self, _key: str, value: float) -> float:
        if value <= 0:
            raise ValueError("SessionQuestion.points_max doit être > 0.")
        return value


# =========================================================================================
# I. Réponses / tentatives
# =========================================================================================


class AnswerCorrectionStatus(str, enum.Enum):
    PENDING = "pending"
    CORRECTED = "corrected"
    FAILED = "failed"


class SessionAnswer(Base):
    """Réponse autosauvegardée pour une SessionQuestion (§ I). Un seul enregistrement par
    SessionQuestion (`session_question_id` unique) : l'autosave « à chaque réponse » du
    ticket met à jour cette ligne en place plutôt que d'empiler un historique de
    tentatives — aucune exigence de multi-tentatives n'est demandée pour la V1.

    `answer_json` est volontairement un JSON générique et versionné (`answer_schema_version`) :
    texte, nombre, choix multiples, classification, ordering, matching, et de futures
    réponses visuelles peuvent tous y être stockés sans nouvelle colonne ni migration."""

    __tablename__ = "v1_session_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_question_id: Mapped[int] = mapped_column(
        ForeignKey("v1_session_questions.id"), unique=True, index=True
    )
    answer_schema_version: Mapped[int] = mapped_column(Integer, default=1)
    answer_json: Mapped[dict | list | str | float] = mapped_column(JSON)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correction_status: Mapped[AnswerCorrectionStatus] = mapped_column(
        Enum(AnswerCorrectionStatus), default=AnswerCorrectionStatus.PENDING
    )
    points_awarded: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    session_question: Mapped["SessionQuestion"] = relationship(back_populates="answer")


# =========================================================================================
# J. Historique question / utilisateur
# =========================================================================================


class UserQuestionHistory(Base):
    """Index dédié « cet utilisateur a-t-il déjà vu cette Question/QuestionVersion ? »
    (§ J) — une ligne par couple (utilisateur, version) mise à jour en place
    (`times_seen`/`last_seen_at`) à chaque nouvelle exposition, plutôt qu'un scan de tout
    `SessionQuestion` à chaque requête de sélection (#41/#43). `question_id` est
    dupliqué depuis la version pour permettre l'exclusion au niveau Question (« déjà vu
    sous une forme ou une autre ») sans jointure supplémentaire, en plus de l'exclusion
    fine par version exacte (nécessaire pour permettre un replay explicite d'un ancien
    questionnaire, § J : « permettre quand même un replay explicite »)."""

    __tablename__ = "v1_user_question_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("v1_users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("v1_questions.id"), index=True)
    question_version_id: Mapped[int] = mapped_column(
        ForeignKey("v1_question_versions.id"), index=True
    )
    session_id: Mapped[int] = mapped_column(ForeignKey("v1_questionnaire_sessions.id"))
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    times_seen: Mapped[int] = mapped_column(Integer, default=1)

    __table_args__ = (
        UniqueConstraint(
            "user_id", "question_version_id", name="uq_v1_user_question_history_version"
        ),
        Index("ix_v1_user_question_history_user_question", "user_id", "question_id"),
    )


# =========================================================================================
# K. Ratings
# =========================================================================================


# Convention Elo-like neutre (voir § K : « algorithme exact sera implémenté dans #45 » —
# uniquement une valeur par défaut raisonnable ici, jamais un choix d'algorithme).
DEFAULT_MODULE_RATING = 1000.0


class UserModuleRating(Base):
    """Rating utilisateur PAR MODULE (§ K — jamais un rating global unique). Un seul
    algorithme de mise à jour sera choisi au ticket #45 ; ce modèle ne fait que fixer la
    forme des données et une valeur par défaut neutre."""

    __tablename__ = "v1_user_module_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("v1_users.id"), index=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), index=True)
    rating: Mapped[float] = mapped_column(Float, default=DEFAULT_MODULE_RATING)
    sessions_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", name="uq_v1_user_module_ratings"),
    )


# =========================================================================================
# L. Feedback utilisateur
# =========================================================================================


class FeedbackType(str, enum.Enum):
    TOO_EASY = "too_easy"
    TOO_HARD = "too_hard"
    AMBIGUOUS = "ambiguous"
    INCORRECT = "incorrect"
    IMAGE_INCORRECT = "image_incorrect"
    ANSWER_DISPUTED = "answer_disputed"
    OTHER = "other"


class QuestionFeedback(Base):
    """Signalement utilisateur sur une Question (§ L), optionnellement pointé sur une
    version précise et/ou une réponse de session donnée quand ce contexte est
    disponible."""

    __tablename__ = "v1_question_feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("v1_users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("v1_questions.id"), index=True)
    question_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("v1_question_versions.id"), nullable=True
    )
    session_answer_id: Mapped[int | None] = mapped_column(
        ForeignKey("v1_session_answers.id"), nullable=True
    )
    feedback_type: Mapped[FeedbackType] = mapped_column(Enum(FeedbackType))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    __table_args__ = (
        Index("ix_v1_question_feedback_question_type", "question_id", "feedback_type"),
    )


# =========================================================================================
# M. Usage IA / quotas
# =========================================================================================


class AIUsage(Base):
    """Suivi d'usage IA par utilisateur et par période (§ M) — le paiement réel n'est pas
    dans ce ticket, seul le compteur est modélisé. `period_key` (« AAAA-MM ») donne une
    granularité mensuelle simple, suffisante pour un quota V1 sans complexifier avec des
    plages de dates — une ligne par (utilisateur, période, fournisseur, modèle), mise à
    jour en place plutôt qu'une ligne par appel."""

    __tablename__ = "v1_ai_usage"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("v1_users.id"), index=True)
    period_key: Mapped[str] = mapped_column(String(7))  # "AAAA-MM"
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_questions: Mapped[int] = mapped_column(Integer, default=0)
    ai_corrections: Mapped[int] = mapped_column(Integer, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "period_key", "provider", "model", name="uq_v1_ai_usage_period"
        ),
        Index("ix_v1_ai_usage_user_period", "user_id", "period_key"),
    )


# =========================================================================================
# N. Génération par module
# =========================================================================================


class ModuleGenerationStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"


class ModuleGenerationConfig(Base):
    """Interrupteur de génération IA par module (§ N), utilisé par les tickets #43/#46."""

    __tablename__ = "v1_module_generation_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), unique=True, index=True)
    generation_status: Mapped[ModuleGenerationStatus] = mapped_column(
        Enum(ModuleGenerationStatus), default=ModuleGenerationStatus.ACTIVE
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


# =========================================================================================
# Helpers de création (résolvent la référence circulaire identité/version courante — voir
# `Question.current_version_id`/`SourceDocument.current_version_id`). Pas une couche de
# service complète : uniquement ce qui est nécessaire pour créer les entités sans violer
# l'invariant « pas de current_version_id orphelin en dehors de l'instant de création ».
# =========================================================================================


def create_question(
    db: Session,
    *,
    module_id: int,
    question_type: str,
    content_json: dict | list,
    generation_source: GenerationSource,
    difficulty_declared: QuestionDifficulty | None = None,
    generator_model: str | None = None,
    prompt_version: str | None = None,
    source_program_version: str | None = None,
    source_document_version_id: int | None = None,
    concepts: list["Concept"] | None = None,
) -> Question:
    """Crée une Question et sa première QuestionVersion (version=1) de façon atomique."""
    question = Question(
        module_id=module_id,
        status=ContentStatus.ACTIVE,
        difficulty_declared=difficulty_declared,
        generation_source=generation_source,
    )
    if concepts:
        question.concepts = list(concepts)
    db.add(question)
    db.flush()

    version = QuestionVersion(
        question_id=question.id,
        version=1,
        question_type=question_type,
        content_json=content_json,
        generator_model=generator_model,
        prompt_version=prompt_version,
        source_program_version=source_program_version,
        source_document_version_id=source_document_version_id,
    )
    db.add(version)
    db.flush()

    question.current_version_id = version.id
    return question


def add_question_version(
    db: Session,
    question: Question,
    *,
    question_type: str,
    content_json: dict | list,
    generator_model: str | None = None,
    prompt_version: str | None = None,
    source_program_version: str | None = None,
    source_document_version_id: int | None = None,
) -> QuestionVersion:
    """Ajoute une nouvelle QuestionVersion à une Question déjà existante et la promeut en
    version courante — ne modifie jamais une QuestionVersion déjà créée."""
    # Requête directe plutôt que `question.versions` : la collection en mémoire n'est
    # rafraîchie qu'au prochain accès après un commit/expire, elle peut donc être
    # périmée si plusieurs versions sont ajoutées dans la même transaction.
    max_version = (
        db.query(QuestionVersion.version)
        .filter_by(question_id=question.id)
        .order_by(QuestionVersion.version.desc())
        .limit(1)
        .scalar()
    )
    next_number = (max_version or 0) + 1
    version = QuestionVersion(
        question_id=question.id,
        version=next_number,
        question_type=question_type,
        content_json=content_json,
        generator_model=generator_model,
        prompt_version=prompt_version,
        source_program_version=source_program_version,
        source_document_version_id=source_document_version_id,
    )
    db.add(version)
    db.flush()

    question.current_version_id = version.id
    return version


def create_source_document(
    db: Session,
    *,
    title: str | None = None,
    content_text: str | None = None,
    content_json: dict | list | None = None,
    module_id: int | None = None,
    asset_id: int | None = None,
) -> SourceDocument:
    """Crée un SourceDocument et sa première SourceDocumentVersion (version=1)."""
    document = SourceDocument(module_id=module_id, status=ContentStatus.ACTIVE)
    db.add(document)
    db.flush()

    version = SourceDocumentVersion(
        source_document_id=document.id,
        version=1,
        title=title,
        content_text=content_text,
        content_json=content_json,
        asset_id=asset_id,
    )
    db.add(version)
    db.flush()

    document.current_version_id = version.id
    return document


def add_source_document_version(
    db: Session,
    document: SourceDocument,
    *,
    title: str | None = None,
    content_text: str | None = None,
    content_json: dict | list | None = None,
    asset_id: int | None = None,
) -> SourceDocumentVersion:
    """Ajoute une nouvelle SourceDocumentVersion et la promeut en version courante."""
    # Requête directe : même raison que dans `add_question_version` ci-dessus.
    max_version = (
        db.query(SourceDocumentVersion.version)
        .filter_by(source_document_id=document.id)
        .order_by(SourceDocumentVersion.version.desc())
        .limit(1)
        .scalar()
    )
    next_number = (max_version or 0) + 1
    version = SourceDocumentVersion(
        source_document_id=document.id,
        version=next_number,
        title=title,
        content_text=content_text,
        content_json=content_json,
        asset_id=asset_id,
    )
    db.add(version)
    db.flush()

    document.current_version_id = version.id
    return version


def record_question_seen(
    db: Session,
    *,
    user_id: int,
    question_version: QuestionVersion,
    session_id: int,
) -> UserQuestionHistory:
    """Enregistre (ou met à jour) qu'un utilisateur a vu une QuestionVersion précise —
    point d'entrée unique pour alimenter `UserQuestionHistory` (§ J), évite la duplication
    de la logique d'upsert à chaque appelant futur (#41/#43)."""
    existing = (
        db.query(UserQuestionHistory)
        .filter_by(user_id=user_id, question_version_id=question_version.id)
        .one_or_none()
    )
    if existing is not None:
        existing.times_seen += 1
        existing.last_seen_at = _utcnow()
        return existing

    entry = UserQuestionHistory(
        user_id=user_id,
        question_id=question_version.question_id,
        question_version_id=question_version.id,
        session_id=session_id,
    )
    db.add(entry)
    db.flush()
    return entry

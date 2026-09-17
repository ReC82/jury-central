"""Ticket #38 — socle de données persistant de l'architecture V1.

Couvre les 16 scénarios minimaux demandés par le ticket, plus quelques invariants
d'intégrité supplémentaires (contraintes uniques, cascades). N'utilise jamais l'IA réelle
(aucun test de ce fichier n'a besoin d'un fournisseur IA — ce ticket pose uniquement le
modèle de données, pas la génération/correction)."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.models import Module, Subject
from app.v1.models import (
    AIUsage,
    Asset,
    AssetKind,
    AssetSourceType,
    Concept,
    ContentStatus,
    FeedbackType,
    GenerationSource,
    ModuleGenerationConfig,
    ModuleGenerationStatus,
    QuestionAsset,
    QuestionFeedback,
    QuestionnaireSession,
    QuestionVersion,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    UserModuleRating,
    UserQuestionHistory,
    UserRole,
    add_question_version,
    add_source_document_version,
    create_question,
    create_source_document,
    record_question_seen,
)


def _module(db_session) -> Module:
    subject = Subject(name="Informatique", slug="informatique-t38")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="AMPCR", slug="ampcr-t38", subject=subject)
    db_session.add(module)
    db_session.flush()
    return module


def _user(db_session, email: str = "eleve@example.test") -> User:
    user = User(email=email, role=UserRole.STUDENT)
    db_session.add(user)
    db_session.flush()
    return user


def _sample_content(prompt: str = "Combien de cœurs a ce CPU ?") -> dict:
    return {
        "schema_version": 1,
        "prompt": prompt,
        "choices": ["2", "4", "8"],
        "correct_indexes": [1],
    }


# --- 1. Création Question + QuestionVersion ----------------------------------------------


def test_create_question_creates_first_version(db_session):
    module = _module(db_session)
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content(),
        generation_source=GenerationSource.AI_GENERATED,
    )
    db_session.commit()
    db_session.expire_all()

    question = db_session.get(type(question), question.id)
    assert question.current_version_id is not None
    assert len(question.versions) == 1
    assert question.versions[0].version == 1
    assert question.current_version.id == question.versions[0].id
    assert question.status == ContentStatus.ACTIVE


# --- 2. Plusieurs versions d'une même question ---------------------------------------------


def test_multiple_versions_of_the_same_question(db_session):
    module = _module(db_session)
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content("v1"),
        generation_source=GenerationSource.MANUAL,
    )
    db_session.flush()

    v2 = add_question_version(
        db_session, question, question_type="single_choice", content_json=_sample_content("v2")
    )
    v3 = add_question_version(
        db_session, question, question_type="single_choice", content_json=_sample_content("v3")
    )
    db_session.commit()
    db_session.expire_all()

    question = db_session.get(type(question), question.id)
    assert [v.version for v in question.versions] == [1, 2, 3]
    assert question.current_version_id == v3.id
    assert v2.version == 2
    assert question.versions[0].content_json["prompt"] == "v1"  # jamais modifié en place


# --- 3. Une ancienne session reste liée à l'ancienne version ------------------------------


def test_old_session_stays_linked_to_old_version_after_new_version_created(db_session):
    module = _module(db_session)
    user = _user(db_session)
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content("original"),
        generation_source=GenerationSource.MANUAL,
    )
    db_session.flush()
    original_version_id = question.current_version_id

    session = QuestionnaireSession(
        user_id=user.id,
        mode=SessionMode.PRACTICE,
        module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM,
    )
    db_session.add(session)
    db_session.flush()
    session_question = SessionQuestion(
        session_id=session.id,
        question_version_id=original_version_id,
        position=1,
        points_max=1.0,
    )
    db_session.add(session_question)
    db_session.commit()

    # La question évolue : nouvelle version, contenu changé.
    add_question_version(
        db_session, question, question_type="single_choice", content_json=_sample_content("edited")
    )
    db_session.commit()
    db_session.expire_all()

    session_question = db_session.get(SessionQuestion, session_question.id)
    assert session_question.question_version_id == original_version_id
    assert session_question.question_version.content_json["prompt"] == "original"


# --- 4. Archivage d'une Question ne détruit rien -------------------------------------------


def test_archiving_a_question_destroys_nothing(db_session):
    module = _module(db_session)
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content(),
        generation_source=GenerationSource.MANUAL,
    )
    add_question_version(
        db_session, question, question_type="single_choice", content_json=_sample_content("v2")
    )
    db_session.commit()
    version_count_before = len(question.versions)

    question.status = ContentStatus.ARCHIVED
    db_session.commit()
    db_session.expire_all()

    question = db_session.get(type(question), question.id)
    assert question.status == ContentStatus.ARCHIVED
    assert len(question.versions) == version_count_before  # rien supprimé


# --- 5. SourceDocument versionné partagé par plusieurs questions --------------------------


def test_source_document_version_shared_by_multiple_questions(db_session):
    module = _module(db_session)
    document = create_source_document(
        db_session, title="Texte argumentatif", content_text="Il était une fois..."
    )
    db_session.flush()
    doc_version_id = document.current_version_id

    q1 = create_question(
        db_session,
        module_id=module.id,
        question_type="short_answer",
        content_json=_sample_content("Résume ce texte."),
        generation_source=GenerationSource.MANUAL,
        source_document_version_id=doc_version_id,
    )
    q2 = create_question(
        db_session,
        module_id=module.id,
        question_type="short_answer",
        content_json=_sample_content("Quel est le thème principal ?"),
        generation_source=GenerationSource.MANUAL,
        source_document_version_id=doc_version_id,
    )
    db_session.commit()
    db_session.expire_all()

    q1 = db_session.get(type(q1), q1.id)
    q2 = db_session.get(type(q2), q2.id)
    assert q1.current_version.source_document_version_id == doc_version_id
    assert q2.current_version.source_document_version_id == doc_version_id

    # Nouvelle version du document : les anciennes QuestionVersion restent sur l'ancienne.
    add_source_document_version(db_session, document, title="Texte argumentatif (relu)")
    db_session.commit()
    db_session.expire_all()
    q1 = db_session.get(type(q1), q1.id)
    assert q1.current_version.source_document_version_id == doc_version_id


# --- 6. Asset réutilisé par plusieurs questions ---------------------------------------------


def test_asset_reused_by_multiple_questions(db_session):
    module = _module(db_session)
    asset = Asset(
        kind=AssetKind.IMAGE,
        storage_ref="/static/v1/schema-cpu.png",
        source_type=AssetSourceType.MANUAL,
    )
    db_session.add(asset)
    db_session.flush()

    q1 = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content(),
        generation_source=GenerationSource.MANUAL,
    )
    q2 = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content("autre question"),
        generation_source=GenerationSource.MANUAL,
    )
    db_session.add(QuestionAsset(question_version_id=q1.current_version_id, asset_id=asset.id))
    db_session.add(QuestionAsset(question_version_id=q2.current_version_id, asset_id=asset.id))
    db_session.commit()

    links = db_session.query(QuestionAsset).filter_by(asset_id=asset.id).all()
    assert len(links) == 2
    assert {link.question_version_id for link in links} == {
        q1.current_version_id,
        q2.current_version_id,
    }


# --- 7. Session avec 10 SessionQuestion ordonnées -------------------------------------------


def test_session_with_ten_ordered_session_questions(db_session):
    module = _module(db_session)
    user = _user(db_session)
    session = QuestionnaireSession(
        user_id=user.id,
        mode=SessionMode.PRACTICE,
        module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM,
        question_count=10,
    )
    db_session.add(session)
    db_session.flush()

    versions = []
    for i in range(10):
        question = create_question(
            db_session,
            module_id=module.id,
            question_type="single_choice",
            content_json=_sample_content(f"Question {i}"),
            generation_source=GenerationSource.MANUAL,
        )
        versions.append(question.current_version_id)

    for position, version_id in enumerate(versions, start=1):
        db_session.add(
            SessionQuestion(
                session_id=session.id,
                question_version_id=version_id,
                position=position,
                points_max=1.0,
            )
        )
    db_session.commit()
    db_session.expire_all()

    session = db_session.get(QuestionnaireSession, session.id)
    assert len(session.session_questions) == 10
    assert [sq.position for sq in session.session_questions] == list(range(1, 11))


# --- 8. Position unique dans une session -----------------------------------------------------


def test_position_unique_within_a_session(db_session):
    module = _module(db_session)
    user = _user(db_session)
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content(),
        generation_source=GenerationSource.MANUAL,
    )
    session = QuestionnaireSession(
        user_id=user.id,
        mode=SessionMode.PRACTICE,
        module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(
        SessionQuestion(
            session_id=session.id,
            question_version_id=question.current_version_id,
            position=1,
            points_max=1.0,
        )
    )
    db_session.commit()

    db_session.add(
        SessionQuestion(
            session_id=session.id,
            question_version_id=question.current_version_id,
            position=1,
            points_max=1.0,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# --- 9. Réponse JSON sauvegardable ------------------------------------------------------------


def test_answer_json_can_be_saved_for_various_shapes(db_session):
    module = _module(db_session)
    user = _user(db_session)
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="classification",
        content_json=_sample_content(),
        generation_source=GenerationSource.MANUAL,
    )
    session = QuestionnaireSession(
        user_id=user.id,
        mode=SessionMode.PRACTICE,
        module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM,
    )
    db_session.add(session)
    db_session.flush()
    session_question = SessionQuestion(
        session_id=session.id,
        question_version_id=question.current_version_id,
        position=1,
        points_max=1.0,
    )
    db_session.add(session_question)
    db_session.flush()

    # Réponse structurée (classification : liste d'indices), pas seulement du texte.
    answer = SessionAnswer(
        session_question_id=session_question.id,
        answer_json=[0, 1, 0, 1, 0],
        duration_seconds=42,
    )
    db_session.add(answer)
    db_session.commit()
    db_session.expire_all()

    session_question = db_session.get(SessionQuestion, session_question.id)
    assert session_question.answer.answer_json == [0, 1, 0, 1, 0]
    assert session_question.answer.correction_status.value == "pending"


# --- 10. Plusieurs sessions simultanées pour un utilisateur --------------------------------


def test_multiple_simultaneous_sessions_for_one_user(db_session):
    module = _module(db_session)
    user = _user(db_session)

    session1 = QuestionnaireSession(
        user_id=user.id,
        mode=SessionMode.PRACTICE,
        module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.EASY,
    )
    session2 = QuestionnaireSession(
        user_id=user.id,
        mode=SessionMode.EXAM,
        module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.HARD,
    )
    db_session.add_all([session1, session2])
    db_session.commit()
    db_session.expire_all()

    sessions = (
        db_session.query(QuestionnaireSession).filter_by(user_id=user.id, status=SessionStatus.IN_PROGRESS).all()
    )
    assert len(sessions) == 2
    assert {s.mode for s in sessions} == {SessionMode.PRACTICE, SessionMode.EXAM}


# --- 11. Historique user/question consultable ------------------------------------------------


def test_user_question_history_is_queryable_and_upserts(db_session):
    module = _module(db_session)
    user = _user(db_session)
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content(),
        generation_source=GenerationSource.MANUAL,
    )
    session = QuestionnaireSession(
        user_id=user.id,
        mode=SessionMode.PRACTICE,
        module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM,
    )
    db_session.add(session)
    db_session.flush()

    record_question_seen(
        db_session, user_id=user.id, question_version=question.current_version, session_id=session.id
    )
    db_session.commit()

    history = (
        db_session.query(UserQuestionHistory)
        .filter_by(user_id=user.id, question_id=question.id)
        .one()
    )
    assert history.times_seen == 1

    # Revu dans une autre session : upsert, pas de doublon.
    record_question_seen(
        db_session, user_id=user.id, question_version=question.current_version, session_id=session.id
    )
    db_session.commit()

    rows = db_session.query(UserQuestionHistory).filter_by(user_id=user.id, question_id=question.id).all()
    assert len(rows) == 1
    assert rows[0].times_seen == 2


# --- 12. Rating utilisateur par module ----------------------------------------------------


def test_user_module_rating_is_per_module_not_global(db_session):
    subject = Subject(name="Informatique", slug="informatique-t38b")
    db_session.add(subject)
    db_session.flush()
    module_a = Module(code="AMPCR", slug="ampcr-t38b", subject=subject)
    module_b = Module(code="RESEAU", slug="reseau-t38b", subject=subject)
    db_session.add_all([module_a, module_b])
    db_session.flush()
    user = _user(db_session)

    db_session.add(UserModuleRating(user_id=user.id, module_id=module_a.id, rating=1050.0))
    db_session.add(UserModuleRating(user_id=user.id, module_id=module_b.id, rating=950.0))
    db_session.commit()
    db_session.expire_all()

    ratings = db_session.query(UserModuleRating).filter_by(user_id=user.id).all()
    assert len(ratings) == 2
    by_module = {r.module_id: r.rating for r in ratings}
    assert by_module[module_a.id] == 1050.0
    assert by_module[module_b.id] == 950.0


def test_user_module_rating_unique_per_user_and_module(db_session):
    module = _module(db_session)
    user = _user(db_session)
    db_session.add(UserModuleRating(user_id=user.id, module_id=module.id))
    db_session.commit()

    db_session.add(UserModuleRating(user_id=user.id, module_id=module.id))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# --- 13. Feedback utilisateur --------------------------------------------------------------


def test_question_feedback_can_be_recorded(db_session):
    module = _module(db_session)
    user = _user(db_session)
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content(),
        generation_source=GenerationSource.MANUAL,
    )
    feedback = QuestionFeedback(
        user_id=user.id,
        question_id=question.id,
        question_version_id=question.current_version_id,
        feedback_type=FeedbackType.AMBIGUOUS,
        comment="Deux réponses semblent correctes.",
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.expire_all()

    stored = db_session.query(QuestionFeedback).filter_by(question_id=question.id).one()
    assert stored.feedback_type == FeedbackType.AMBIGUOUS
    assert stored.comment == "Deux réponses semblent correctes."


# --- 14. Usage IA / quota -----------------------------------------------------------------


def test_ai_usage_accumulates_per_period(db_session):
    user = _user(db_session)
    usage = AIUsage(
        user_id=user.id,
        period_key="2026-09",
        provider="openai",
        model="gpt-4o-mini",
        generated_questions=5,
        input_tokens=1200,
        output_tokens=800,
        estimated_cost=0.02,
    )
    db_session.add(usage)
    db_session.commit()

    stored = db_session.query(AIUsage).filter_by(user_id=user.id, period_key="2026-09").one()
    assert stored.generated_questions == 5
    assert stored.input_tokens == 1200


def test_ai_usage_unique_per_user_period_provider_model(db_session):
    user = _user(db_session)
    db_session.add(AIUsage(user_id=user.id, period_key="2026-09", provider="openai", model="gpt-4o-mini"))
    db_session.commit()

    db_session.add(AIUsage(user_id=user.id, period_key="2026-09", provider="openai", model="gpt-4o-mini"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# --- 15./16. Migrations additives sur DB existante synthétique + idempotence --------------


def test_additive_migration_on_pre_existing_synthetic_database(tmp_path):
    """Simule un staging pré-#38 (seules les 4 tables historiques existent, avec des
    données), applique la création des tables V1 par-dessus (comme le ferait un vrai
    déploiement), et vérifie qu'aucune donnée existante n'est perturbée."""
    from app import models as legacy_models  # noqa: F401 — enregistre les tables historiques
    from app.database import Base
    from app.v1 import models as v1_models  # noqa: F401 — enregistre les tables V1

    db_path = tmp_path / "pre_v38.db"
    engine = create_engine(f"sqlite:///{db_path}")
    legacy_tables = [
        Base.metadata.tables[name]
        for name in ("subjects", "modules", "uaas", "lesson_blocks")
    ]

    # État "pré-#38" : uniquement les tables historiques, avec une ligne représentative.
    Base.metadata.create_all(bind=engine, tables=legacy_tables)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.execute(
        Subject.__table__.insert().values(id=1, name="Informatique", slug="informatique-legacy")
    )
    session.commit()
    session.close()

    with engine.connect() as connection:
        existing_tables = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert "v1_users" not in existing_tables

    # Déploiement #38 : create_all (idempotent, checkfirst=True par défaut) ajoute les
    # tables V1 manquantes sans toucher aux tables/lignes déjà présentes.
    Base.metadata.create_all(bind=engine)

    with engine.connect() as connection:
        tables_after_first_pass = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        subject_row = connection.exec_driver_sql(
            "SELECT name, slug FROM subjects WHERE id=1"
        ).fetchone()

    assert "v1_users" in tables_after_first_pass
    assert "v1_questions" in tables_after_first_pass
    assert "v1_session_answers" in tables_after_first_pass
    assert subject_row == ("Informatique", "informatique-legacy")  # donnée intacte

    # Second passage : idempotent, aucune erreur, aucun changement.
    Base.metadata.create_all(bind=engine)

    with engine.connect() as connection:
        tables_after_second_pass = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        subject_count = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM subjects"
        ).fetchone()[0]

    assert tables_after_second_pass == tables_after_first_pass
    assert subject_count == 1  # pas de duplication

    engine.dispose()


# --- Intégrité supplémentaire : contraintes, cascades ---------------------------------------


def test_question_version_unique_per_question_and_version_number(db_session):
    module = _module(db_session)
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content(),
        generation_source=GenerationSource.MANUAL,
    )
    db_session.commit()

    db_session.add(
        QuestionVersion(
            question_id=question.id, version=1, question_type="single_choice",
            content_json=_sample_content("doublon"),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_question_version_number_must_be_positive():
    with pytest.raises(ValueError):
        QuestionVersion(question_id=1, version=0, question_type="single_choice", content_json={})


def test_session_question_points_max_must_be_positive():
    with pytest.raises(ValueError):
        SessionQuestion(session_id=1, question_version_id=1, position=1, points_max=0)


def test_session_is_locked_only_when_not_in_progress():
    # `status` explicite : le défaut de colonne ne s'applique qu'au flush, pas à la
    # construction Python de l'objet — voir `QuestionnaireSession.status`.
    session = QuestionnaireSession(
        user_id=1, mode=SessionMode.PRACTICE, module_id=1,
        difficulty_requested=SessionDifficultyRequest.MEDIUM,
        status=SessionStatus.IN_PROGRESS,
    )
    assert session.is_locked() is False
    session.status = SessionStatus.COMPLETED
    assert session.is_locked() is True
    session.status = SessionStatus.ABANDONED
    assert session.is_locked() is True


def test_deleting_session_cascades_to_its_own_questions_but_not_to_question_version(db_session):
    """Cascade appropriée : supprimer une session supprime ses SessionQuestion/
    SessionAnswer (qui n'ont pas de sens hors session), mais ne touche jamais la
    QuestionVersion partagée (banque persistante, jamais en cascade)."""
    module = _module(db_session)
    user = _user(db_session)
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="single_choice",
        content_json=_sample_content(),
        generation_source=GenerationSource.MANUAL,
    )
    session = QuestionnaireSession(
        user_id=user.id, mode=SessionMode.PRACTICE, module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM,
    )
    db_session.add(session)
    db_session.flush()
    session_question = SessionQuestion(
        session_id=session.id, question_version_id=question.current_version_id,
        position=1, points_max=1.0,
    )
    db_session.add(session_question)
    db_session.flush()
    db_session.add(SessionAnswer(session_question_id=session_question.id, answer_json={"choice": 1}))
    db_session.commit()

    version_id = question.current_version_id
    session_question_id = session_question.id

    db_session.delete(session)
    db_session.commit()
    db_session.expire_all()

    assert db_session.get(SessionQuestion, session_question_id) is None
    assert db_session.get(QuestionVersion, version_id) is not None  # jamais supprimée


def test_module_generation_config_defaults_active(db_session):
    module = _module(db_session)
    config = ModuleGenerationConfig(module_id=module.id)
    db_session.add(config)
    db_session.commit()
    db_session.expire_all()

    stored = db_session.query(ModuleGenerationConfig).filter_by(module_id=module.id).one()
    assert stored.generation_status == ModuleGenerationStatus.ACTIVE


def test_concept_can_be_attached_to_multiple_questions(db_session):
    module = _module(db_session)
    concept = Concept(code="ram", label="Mémoire vive (RAM)")
    db_session.add(concept)
    db_session.flush()

    q1 = create_question(
        db_session, module_id=module.id, question_type="single_choice",
        content_json=_sample_content(), generation_source=GenerationSource.MANUAL,
        concepts=[concept],
    )
    q2 = create_question(
        db_session, module_id=module.id, question_type="single_choice",
        content_json=_sample_content("autre"), generation_source=GenerationSource.MANUAL,
        concepts=[concept],
    )
    db_session.commit()
    db_session.expire_all()

    concept = db_session.get(Concept, concept.id)
    assert {q.id for q in concept.questions} == {q1.id, q2.id}

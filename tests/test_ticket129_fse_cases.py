"""Ticket #129 — FSE : cas nouveaux et vrais supports visuels en entraînement et examen.

Garanties vérifiées (aucun appel IA ni génération d'image réels) :
- import des cas FSE01 additif et idempotent, sans bloquer ni dupliquer la banque historique ;
- texte affiché = extraits exacts du document transmis à la correction ;
- l'affiche est une vraie composition (illustration servie + texte HTML), jamais une
  description entre crochets ;
- deux sessions successives : cas nouveaux d'abord, aucune question répétée, exemples du
  cours seulement en complément ; un cas déjà vu passe après un cas jamais vu ;
- difficulté toujours prioritaire ; matières sans exemples déclarés inchangées ;
- visuel indisponible → questions du cas non servies ; fichier absent → cas non importé ;
- reprise : mêmes questions, même version de document, aucun appel de génération ;
- FSE17 : reprend les nouveaux cas et couvre plusieurs cours.
"""

import html
import random
import re
from types import SimpleNamespace

import pytest

from app.models import UAA, Module
from app.seed import seed
from app.templating import templates
from app.v1 import document_layouts as dl
from app.v1 import fse_cases
from app.v1.correction_worker import _UnconfiguredProvider
from app.v1.francais_fr01_05_bank import import_francais_fr01_to_bank
from app.v1.francais_plan import FRANCAIS_MODULE_CODE
from app.v1.fse01_cases import (
    CHAT_TITLE,
    FSE01_CASES,
    MEMO_TITLE,
    POSTER_TITLE,
)
from app.v1.fse_bank import (
    import_fse01_to_bank,
    import_fse05_to_bank,
    import_fse06_to_bank,
    import_fse07_to_bank,
    import_fse08_to_bank,
    import_fse09_to_bank,
    import_fse10_to_bank,
    import_fse11_to_bank,
    import_fse12_to_bank,
    import_fse13_to_bank,
    import_fse14_to_bank,
    import_fse15_to_bank,
    import_fse16_to_bank,
)
from app.v1.fse_cases import (
    COURSE_EXAMPLE,
    FRESH,
    SEEN_CASE,
    case_ranker,
    import_fse_cases,
    is_course_example,
)
from app.v1.fse_plan import FSE_MODULE_CODE
from app.v1.models import (
    Asset,
    ContentStatus,
    GenerationSource,
    Question,
    QuestionDifficulty,
    SessionDifficultyRequest,
    SessionMode,
    SourceDocumentVersion,
    User,
)
from app.v1.session_service import build_question_display, compose_selection, start_session

FSE01_SLUG = "fse-fse01"
CASE_QUESTIONS = sum(len(case.questions) for case in FSE01_CASES)


def _user(db_session, email):
    user = User(email=email, password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    return user


def _fse01(db_session, *, with_cases=True):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, module, uaa)
    if with_cases:
        import_fse_cases(db_session, module, uaa)
    db_session.commit()
    return module, uaa


def _start(db_session, module, uaa, user, *, mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.ADAPTIVE, count=10):
    return start_session(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="FSE01", mode=mode,
        difficulty=difficulty, provider=_UnconfiguredProvider(), question_count=count,
    )


def _questions(session):
    return [sq.question_version.question for sq in sorted(session.session_questions, key=lambda sq: sq.position)]


def _render(doc):
    module = templates.env.get_template("_document_layouts.html").module
    return str(module.render(doc, "Document de référence", uid="t"))


# --- Import -------------------------------------------------------------------------------


def test_cases_import_is_additive_idempotent_and_does_not_block_the_historical_bank(db_session):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    # Cas importés AVANT la banque historique : celle-ci doit quand même s'importer.
    assert import_fse_cases(db_session, module, uaa) == CASE_QUESTIONS == 17
    assert import_fse01_to_bank(db_session, module, uaa) == 14
    assert import_fse_cases(db_session, module, uaa) == 0
    assert import_fse01_to_bank(db_session, module, uaa) == 0
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert len(questions) == 31
    manual = [q for q in questions if q.generation_source == GenerationSource.MANUAL]
    assert len(manual) == 17
    assert all(q.difficulty_declared is not None for q in manual)
    titles = {
        row[0] for row in db_session.query(SourceDocumentVersion.title).filter(
            SourceDocumentVersion.title.in_([POSTER_TITLE, CHAT_TITLE, MEMO_TITLE])
        )
    }
    assert titles == {POSTER_TITLE, CHAT_TITLE, MEMO_TITLE}
    # Chaque question de cas à document référence une version réellement persistée.
    for question in manual:
        doc_id = question.current_version.content_json.get("source_document_version_id")
        if doc_id:
            assert question.current_version.source_document_version_id == doc_id
            assert db_session.get(SourceDocumentVersion, doc_id) is not None


def test_difficulties_are_spread_across_new_cases():
    counts = {d: 0 for d in QuestionDifficulty}
    for case in FSE01_CASES:
        for _type, _content, difficulty in case.questions:
            counts[difficulty] += 1
    assert counts[QuestionDifficulty.EASY] == 5
    assert counts[QuestionDifficulty.MEDIUM] == 7
    assert counts[QuestionDifficulty.HARD] == 5


@pytest.mark.parametrize("case", fse_cases.all_cases(), ids=lambda c: c.key)
def test_new_cases_do_not_reuse_course_examples(case):
    text = " ".join([case.title or "", case.content_text or ""] + [str(q[1]) for q in case.questions])
    examples = fse_cases.course_examples()[case.course_code]
    for marker in examples.markers:
        assert marker not in text, (case.key, marker)
    assert case.title not in examples.document_titles
    for marker in ("Karim", "Techno Services", "sécurité routière", "Dufresne", "SPW"):
        assert marker not in text, (case.key, marker)


def test_every_course_with_cases_spreads_difficulties():
    for code in [f"FSE{n:02d}" for n in range(1, 17)]:
        levels = {d for case in fse_cases.cases_for(code) for _t, _c, d in case.questions}
        assert levels == set(QuestionDifficulty), code


# --- Texte exact, affiche composée ---------------------------------------------------------


@pytest.mark.parametrize("case", [c for c in fse_cases.all_cases() if c.layout], ids=lambda c: c.key)
def test_layout_text_is_verbatim_and_covers_the_document(case):
    corpus = dl.verification_corpus(case.title, case.content_text, case.layout)
    for fragment in dl.iter_content_strings(case.layout):
        assert dl.comparable(fragment) in corpus, fragment
    words = set(re.findall(r"\w{4,}", dl.comparable(re.sub(r"^\[.*?\]\s*", "", case.content_text, flags=re.DOTALL))))
    shown = " ".join(dl.comparable(s) for s in dl.iter_content_strings(case.layout))
    # Description de l'illustration : affichée sous l'affiche et en texte alternatif.
    shown += " " + dl.comparable(case.layout.get("image_alt", ""))
    labels = {"haut", "affiche", "bandeau", "titre", "grandes", "lettres", "illustration", "dessin",
              "date", "lieu", "objets", "acceptés", "sous", "note", "service", "dernier", "message",
              "nadia", "application", "indique", "encadré", "règle", "magazine", "principal",
              "couverture", "premiers", "résultats", "trouvés", "commentaires", "affichés",
              "publication", "infos", "pays", "vert", "vallée", "page", "recettes", "rédigée", "remise"}
    missing = {w for w in words if w not in shown and w not in labels}
    assert not missing, missing


def test_poster_is_a_real_composition_with_an_illustration(db_session):
    _fse01(db_session)
    version = db_session.query(SourceDocumentVersion).filter_by(title=POSTER_TITLE).one()
    assert version.asset is not None
    assert version.asset.storage_ref == "img/fse/cases/fse01_atelier_reparation.svg"
    metadata = version.asset.metadata_json
    assert metadata["sha256"] and metadata["prompt"] and metadata["production"] == "svg_hand_authored"
    assert dl.resolve_layout(version)["kind"] == "poster_sheet"
    html = _render(version)
    assert 'src="/static/img/fse/cases/fse01_atelier_reparation.svg"' in html
    assert "TON VÉLO GRINCE ? ON LE RÉPARE ENSEMBLE !" in html
    assert "jc-zoomable" in html and "Ouvrir en grand" in html
    assert "Affiche au format A3" in html  # contexte d'installation, à part
    assert "[" not in re.sub(r"<[^>]+>", "", html)  # aucune description entre crochets
    assert "logo fictif" not in html.lower() and "image ici" not in html.lower()


def test_chat_read_status_and_memo_context_are_rendered(db_session):
    _fse01(db_session)
    chat = db_session.query(SourceDocumentVersion).filter_by(title=CHAT_TITLE).one()
    html = _render(chat)
    assert "Lu par 8 des 12 membres du groupe" in html and "Salle B du HALL OMNISPORTS" in html
    memo = db_session.query(SourceDocumentVersion).filter_by(title=MEMO_TITLE).one()
    html = _render(memo)
    assert "Trois étudiants jobistes commencent ce samedi" in html and "N+1" in html


def test_session_page_shows_the_poster_and_document_page_is_printable(authenticated_client, db_session, monkeypatch):
    module, uaa = _fse01(db_session)
    monkeypatch.setattr(
        "app.v1.routes_sessions.get_ai_provider", lambda: (_ for _ in ()).throw(AssertionError("aucune IA"))
    )
    user = db_session.query(User).filter_by(email="eleve-test@example.test").one()
    session = _start(db_session, module, uaa, user, mode=SessionMode.EXAM, count=17)
    position = next(
        sq.position for sq in session.session_questions
        if sq.source_document_version is not None and sq.source_document_version.title == POSTER_TITLE
    )
    response = authenticated_client.get(f"/sessions/{session.id}?q={position}")
    assert response.status_code == 200
    assert "fse01_atelier_reparation.svg" in response.text
    assert "TON VÉLO GRINCE" in response.text
    version = db_session.query(SourceDocumentVersion).filter_by(title=POSTER_TITLE).one()
    page = authenticated_client.get(f"/documents/{version.id}")
    assert page.status_code == 200
    assert "fse01_atelier_reparation.svg" in page.text and "Imprimer" in page.text


# --- Sélection : cas nouveaux d'abord ------------------------------------------------------


def test_course_example_detection(db_session):
    _module, uaa = _fse01(db_session)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    examples = [q for q in questions if is_course_example(q)]
    # 8 questions historiques sur le mail, l'affiche et la publication du cours (dont le
    # classement des trois canaux, sans document rattaché mais qui les cite).
    assert len(examples) == 8
    assert not any(q.generation_source == GenerationSource.MANUAL for q in examples)


def test_successive_sessions_serve_new_cases_first_without_repetition(db_session):
    module, uaa = _fse01(db_session)
    user = _user(db_session, "fse129-two@example.invalid")
    sessions = [_questions(_start(db_session, module, uaa, user)) for _ in range(3)]
    assert [len(s) for s in sessions] == [10, 10, 10]
    ids = [q.id for s in sessions for q in s]
    assert len(ids) == len(set(ids)), "aucune question répétée d'une session à l'autre"
    # 23 questions hors exemples du cours : les deux premières sessions n'en contiennent
    # aucun ; les exemples ne complètent que la troisième, une fois les cas nouveaux épuisés.
    assert [sum(1 for q in s if is_course_example(q)) for s in sessions] == [0, 0, 7]
    for session in sessions[:2]:
        titles = {q.current_version.source_document_version.title for q in session if q.current_version.source_document_version}
        assert titles & {POSTER_TITLE, CHAT_TITLE, MEMO_TITLE}


def test_already_seen_case_ranks_after_unseen_case(db_session):
    module, uaa = _fse01(db_session)
    user = _user(db_session, "fse129-rank@example.invalid")
    served = _questions(_start(db_session, module, uaa, user, count=4))
    served_ids = {q.id for q in served}
    served_docs = {
        q.current_version.source_document_version.source_document_id
        for q in served if q.current_version.source_document_version is not None
    }
    rank = case_ranker(db_session, user_id=user.id)
    others = [
        q for q in db_session.query(Question).filter_by(uaa_id=uaa.id)
        if q.id not in served_ids and not is_course_example(q)
        and q.current_version.source_document_version is not None
    ]
    seen_case = [q for q in others if q.current_version.source_document_version.source_document_id in served_docs]
    unseen_case = [q for q in others if q.current_version.source_document_version.source_document_id not in served_docs]
    assert seen_case and all(rank(q) == SEEN_CASE for q in seen_case)
    assert all(rank(q) == FRESH for q in unseen_case)
    example = next(q for q in db_session.query(Question).filter_by(uaa_id=uaa.id) if is_course_example(q))
    assert rank(example) == COURSE_EXAMPLE


def test_difficulty_stays_prior_to_case_freshness(db_session):
    module, uaa = _fse01(db_session)
    user = _user(db_session, "fse129-hard@example.invalid")
    session = _start(db_session, module, uaa, user, difficulty=SessionDifficultyRequest.HARD)
    questions = _questions(session)
    hard = [q for q in questions if q.difficulty_declared == QuestionDifficulty.HARD]
    # 8 questions difficiles en banque, dont 6 à réponse longue (plafond : 3 par session) :
    # 5 servables, toutes prises — et ce sont les nouveaux cas qui passent en premier.
    assert len(hard) == 5
    assert all(q.generation_source == GenerationSource.MANUAL for q in hard)


def test_rank_is_a_strict_no_op_when_all_ranks_are_equal(db_session):
    _module, uaa = _fse01(db_session, with_cases=False)
    pool = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    random.seed(129)
    without = [q.id for q in compose_selection(list(pool), 10, SessionDifficultyRequest.MEDIUM)]
    random.seed(129)
    with_rank = [q.id for q in compose_selection(list(pool), 10, SessionDifficultyRequest.MEDIUM, rank_fn=lambda q: 0)]
    assert without == with_rank


def test_subjects_without_declared_examples_rank_everything_fresh(db_session):
    seed()
    # Tous les cours FSE01→FSE16 déclarent leurs exemples : contrôle sur le Français.
    module = db_session.query(Module).filter_by(code=FRANCAIS_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug="francais-fr01").first()
    assert import_francais_fr01_to_bank(db_session, module, uaa) > 0
    rank = case_ranker(db_session, user_id=1)
    assert {rank(q) for q in db_session.query(Question).filter_by(uaa_id=uaa.id)} == {FRESH}


# --- Visuel indisponible, reprise ----------------------------------------------------------


def test_case_with_missing_illustration_is_not_imported(db_session, monkeypatch):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    poster = FSE01_CASES[0]
    broken = SimpleNamespace(**poster.__dict__)
    broken.illustration = poster.illustration.__class__(
        **{**poster.illustration.__dict__, "storage_ref": "img/fse/cases/absent.svg"}
    )
    monkeypatch.setattr(fse_cases, "cases_for", lambda code: (broken, *FSE01_CASES[1:]))
    created = import_fse_cases(db_session, module, uaa)
    assert created == CASE_QUESTIONS - len(poster.questions)
    assert db_session.query(SourceDocumentVersion).filter_by(title=POSTER_TITLE).count() == 0


def test_questions_of_an_unusable_illustration_are_never_served(db_session):
    module, uaa = _fse01(db_session)
    version = db_session.query(SourceDocumentVersion).filter_by(title=POSTER_TITLE).one()
    asset = db_session.get(Asset, version.asset_id)
    asset.status = ContentStatus.INVALID
    db_session.commit()
    user = _user(db_session, "fse129-invalid@example.invalid")
    served = _questions(_start(db_session, module, uaa, user, count=31))
    assert served
    assert not [
        q for q in served
        if q.current_version.source_document_version_id == version.id
    ]


def test_resume_keeps_same_questions_and_document_versions_without_any_generation(db_session, monkeypatch):
    module, uaa = _fse01(db_session)

    def _forbidden(*_args, **_kwargs):
        raise AssertionError("aucune génération d'image à l'affichage ou à la reprise")

    monkeypatch.setattr("app.ai.factory.get_image_provider", _forbidden)
    user = _user(db_session, "fse129-resume@example.invalid")
    session = _start(db_session, module, uaa, user, count=17)
    before = [(sq.question_version_id, build_question_display(db_session, sq)) for sq in session.session_questions]
    db_session.expire_all()
    from app.v1.models import QuestionnaireSession

    reloaded = db_session.get(QuestionnaireSession, session.id)
    after = [(sq.question_version_id, build_question_display(db_session, sq)) for sq in reloaded.session_questions]
    assert [q for q, _ in before] == [q for q, _ in after]
    assert [repr(d) for _, d in before] == [repr(d) for _, d in after]


# --- FSE17 ---------------------------------------------------------------------------------


def test_fse17_mock_exam_reuses_new_cases_and_covers_several_courses(authenticated_client, db_session, monkeypatch):
    seed()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: _UnconfiguredProvider())
    # Ouvrir l'examen blanc amorce les banques et les cas nouveaux de FSE01→FSE16.
    assert authenticated_client.get("/uaa/fse-fse17/exam").status_code == 200
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    fse17 = db_session.query(UAA).filter_by(slug="fse-fse17").first()
    total_cases = sum(len(case.questions) for case in fse_cases.all_cases())
    assert db_session.query(Question).filter_by(generation_source=GenerationSource.MANUAL).count() == total_cases
    user = _user(db_session, "fse129-fse17@example.invalid")
    session = start_session(
        db_session, user=user, module_id=module.id, uaa_id=fse17.id, uaa_code="FSE17",
        mode=SessionMode.EXAM, difficulty=SessionDifficultyRequest.ADAPTIVE,
        provider=_UnconfiguredProvider(), question_count=20,
    )
    questions = _questions(session)
    assert len(questions) == 20
    assert len({q.uaa.code for q in questions}) >= 4
    fse01 = [q for q in questions if q.uaa.code == "FSE01"]
    assert not [q for q in fse01 if is_course_example(q)]


# --- Lots FSE05→FSE08, FSE09→FSE12 et FSE13→FSE16 -------------------------------------------

_BANK_IMPORTERS = {
    "FSE05": import_fse05_to_bank, "FSE06": import_fse06_to_bank,
    "FSE07": import_fse07_to_bank, "FSE08": import_fse08_to_bank,
    "FSE09": import_fse09_to_bank, "FSE10": import_fse10_to_bank,
    "FSE11": import_fse11_to_bank, "FSE12": import_fse12_to_bank,
    "FSE13": import_fse13_to_bank, "FSE14": import_fse14_to_bank,
    "FSE15": import_fse15_to_bank, "FSE16": import_fse16_to_bank,
}


@pytest.mark.parametrize("code", sorted(_BANK_IMPORTERS))
def test_fse05_to_fse08_cases_are_imported_ranked_and_served_first(db_session, code):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug=f"fse-{code.lower()}").first()
    bank = _BANK_IMPORTERS[code](db_session, module, uaa)
    expected = sum(len(case.questions) for case in fse_cases.cases_for(code))
    assert import_fse_cases(db_session, module, uaa) == expected
    assert import_fse_cases(db_session, module, uaa) == 0
    db_session.commit()
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert len(questions) == bank + expected
    rank = case_ranker(db_session, user_id=1)
    manual = [q for q in questions if q.generation_source == GenerationSource.MANUAL]
    assert {rank(q) for q in manual} == {FRESH}
    # Les documents commentés dans le cours sont reconnus comme exemples du cours.
    assert any(rank(q) == COURSE_EXAMPLE for q in questions if q.generation_source != GenerationSource.MANUAL)
    user = _user(db_session, f"fse129-{code.lower()}@example.invalid")
    session = start_session(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code=code,
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.ADAPTIVE,
        provider=_UnconfiguredProvider(), question_count=10,
    )
    served = _questions(session)
    assert len(served) == 10 and len({q.id for q in served}) == 10
    # Cas nouveaux (et questions sans document) avant les exemples commentés du cours.
    fresh_pool = [q for q in questions if rank(q) == FRESH]
    assert len(fresh_pool) >= 10
    assert not [q for q in served if is_course_example(q)], code
    assert any(q.generation_source == GenerationSource.MANUAL for q in served)


@pytest.mark.parametrize(
    "case", [c for c in fse_cases.all_cases() if c.layout and c.course_code >= "FSE05"], ids=lambda c: c.key
)
def test_fse05_to_fse08_documents_render_without_placeholder(db_session, case):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug=f"fse-{case.course_code.lower()}").first()
    import_fse_cases(db_session, module, uaa)
    db_session.commit()
    version = db_session.query(SourceDocumentVersion).filter_by(title=case.title).one()
    assert dl.resolve_layout(version)["kind"] == case.layout["kind"]
    text = html.unescape(re.sub(r"<[^>]+>", " ", _render(version)))
    assert "[" not in text  # aucune description entre crochets
    shown = dl.comparable(text)
    for fragment in dl.iter_content_strings(case.layout):
        assert dl.comparable(fragment) in shown, fragment

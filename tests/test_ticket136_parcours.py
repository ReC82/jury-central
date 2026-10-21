"""Ticket #136 — parcours Diplôme → Forme → Option, « Mon parcours », chemin de cours et
progression réelle. Aucune IA : sessions construites directement en base."""

import re

import pytest

from app.models import UAA, BlockSpace, BlockType, LessonBlock, Module, Subject
from app.v1.models import (
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    UserPathway,
    create_question,
)
from app.v1.parcours import resolve_keys, user_uaa_progress

# --- Helpers ---------------------------------------------------------------------------------


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match
    return match.group(1)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).replace("&nbsp;", "\u00a0")


def _content(db):
    """Matières du parcours AMPCR + Mathématiques (hors parcours), codes de module réels."""
    out = {}
    for name, slug, code, uaa_codes in (
        ("Informatique", "informatique", "AMPCR", ("MC01", "MC02")),
        ("Français", "francais", "FRANCAIS", ("FR01",)),
        ("Formation sociale et économique", "formation-sociale-et-economique", "FSE", ("FSE01",)),
        ("Mathématiques", "mathematiques", "MB32", ("UAA1",)),
    ):
        subject = Subject(name=name, slug=slug)
        db.add(subject)
        db.flush()
        module = Module(code=code, slug=code.lower(), subject_id=subject.id)
        db.add(module)
        db.flush()
        uaas = []
        for position, uaa_code in enumerate(uaa_codes, start=1):
            uaa = UAA(
                code=uaa_code, title=f"Cours {uaa_code}", slug=f"t136-{uaa_code.lower()}",
                position=position, is_published=True, module_id=module.id,
            )
            db.add(uaa)
            uaas.append(uaa)
        db.flush()
        out[code] = (module, uaas)
    db.add(LessonBlock(
        uaa_id=out["MB32"][1][0].id, title="Cours", type=BlockType.MARKDOWN,
        content="## A\n\ntexte", position=1, space=BlockSpace.COURSE,
    ))
    db.commit()
    return out


def _choose(client, diploma="cess", form="p", option="ampcr"):
    token = _csrf(client.get("/parcours?diplome=cess&forme=p").text)
    return client.post(
        "/parcours/choisir",
        data={"csrf_token": token, "diploma": diploma, "form": form, "option": option},
        follow_redirects=False,
    )


def _session(db, user, module, uaa, *, mode, status, score=None, count=10, scope=None):
    question = create_question(
        db, module_id=module.id, uaa_id=uaa.id, question_type="short_answer",
        content_json={"prompt": "Question #136 ?", "rubric": "Grille."},
        generation_source="manual",
    )
    session = QuestionnaireSession(
        user_id=user.id, mode=mode, module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=status,
        question_count=count, score=score,
        parameters_json={"scope": scope} if scope else {"severity": 3},
    )
    db.add(session)
    db.flush()
    db.add(SessionQuestion(
        session_id=session.id, question_version_id=question.current_version_id,
        position=1, points_max=1.0,
    ))
    db.commit()
    return session


# --- Registre ----------------------------------------------------------------------------------


def test_registry_resolves_only_available_options():
    pathway = resolve_keys("cess", "p", "ampcr")
    assert pathway is not None
    assert [t.module_code for t in pathway.option.tracks] == ["AMPCR", "FRANCAIS", "FSE"]
    assert pathway.option.tracks[0].role == "option"
    assert resolve_keys("cess", "g", "ampcr") is None  # forme sans contenu
    assert resolve_keys("cess", "p", "inconnue") is None
    assert resolve_keys(None, None, None) is None


# --- Accueil / navigation ----------------------------------------------------------------------


def test_home_invites_to_choose_and_header_has_no_practice_link(client):
    page = client.get("/").text
    assert 'href="/parcours"' in page
    assert "Choisir mon parcours" in page
    assert "en cours de construction" not in page
    assert 'href="/practice/equations"' not in page  # #67 § A : retiré du header
    assert 'href="/mon-parcours"' in page
    # La route historique reste servie (lien direct conservé)
    assert client.get("/practice/equations").status_code == 200


def test_wizard_steps_show_unavailable_forms_without_links(client, db_session):
    _content(db_session)
    assert "CESS" in client.get("/parcours").text
    step2 = client.get("/parcours?diplome=cess").text
    assert 'href="/parcours?diplome=cess&amp;forme=p"' in step2
    assert "forme=g" not in step2 and "CESS G" in step2  # affiché, non cliquable
    step3 = client.get("/parcours?diplome=cess&forme=p").text
    assert 'name="option" value="ampcr"' in step3
    assert "Assistant/Assistante de maintenance PC-réseaux" in step3
    # Forme indisponible → retombe sur l'étape 2, jamais un faux choix
    assert 'name="option"' not in client.get("/parcours?diplome=cess&forme=g").text


def test_mon_parcours_redirects_to_wizard_until_chosen(client):
    response = client.get("/mon-parcours", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/parcours"


def test_anonymous_choice_is_remembered_and_dashboard_is_honest(client, db_session):
    _content(db_session)
    response = _choose(client)
    assert response.status_code == 303
    assert response.headers["location"] == "/mon-parcours"
    page = _text(client.get("/mon-parcours").text)
    assert "Informatique — maintenance PC-réseaux" in page
    assert "Français" in page and "Formation sociale et économique" in page
    assert "2 cours disponibles sur 38 prévus" in page.replace("  ", " ")  # pas de faux cours
    assert "MC01 — Cours MC01" in page  # prochaine étape = premier cours de l'option
    assert "Mathématiques — MB32" in page  # hors parcours, signalé comme tel
    assert "ni une note officielle" in page
    # Accueil : « Continuer » une fois le parcours mémorisé
    assert "Continuer mon parcours" in client.get("/").text


def test_choice_requires_valid_csrf_and_known_keys(client, db_session):
    _content(db_session)
    client.get("/parcours")
    bad = client.post(
        "/parcours/choisir",
        data={"csrf_token": "faux", "diploma": "cess", "form": "p", "option": "ampcr"},
        follow_redirects=False,
    )
    assert bad.headers["location"] == "/parcours"
    assert client.get("/mon-parcours", follow_redirects=False).status_code == 303
    unknown = _choose(client, option="admin-reseau")
    assert unknown.headers["location"] == "/parcours"


def test_logged_in_choice_is_stored_once_and_change_keeps_progress(
    authenticated_client, db_session
):
    content = _content(db_session)
    user = db_session.query(User).filter_by(email="eleve-test@example.test").one()
    module, uaas = content["AMPCR"]
    _session(db_session, user, module, uaas[0], mode=SessionMode.PRACTICE,
             status=SessionStatus.COMPLETED, score=7)
    _choose(authenticated_client)
    _choose(authenticated_client)
    rows = db_session.query(UserPathway).filter_by(user_id=user.id).all()
    assert len(rows) == 1 and rows[0].option_key == "ampcr"
    assert db_session.query(QuestionnaireSession).filter_by(user_id=user.id).count() == 1


def test_choice_made_before_login_is_attached_to_account(client, db_session):
    _content(db_session)
    _choose(client)
    token = _csrf(client.get("/register").text)
    client.post("/register", data={
        "csrf_token": token, "email": "t136@example.test", "password": "test-password-1234",
        "password_confirm": "test-password-1234", "display_name": "T136",
    })
    assert client.get("/mon-parcours").status_code == 200
    user = db_session.query(User).filter_by(email="t136@example.test").one()
    assert db_session.query(UserPathway).filter_by(user_id=user.id).count() == 1


# --- Progression réelle -------------------------------------------------------------------------


def test_progress_distinguishes_practice_exam_and_in_progress(authenticated_client, db_session):
    content = _content(db_session)
    user = db_session.query(User).filter_by(email="eleve-test@example.test").one()
    module, (mc01, mc02) = content["AMPCR"]
    _session(db_session, user, module, mc01, mode=SessionMode.PRACTICE,
             status=SessionStatus.COMPLETED, score=4)
    _session(db_session, user, module, mc01, mode=SessionMode.EXAM,
             status=SessionStatus.COMPLETED, score=6)
    _session(db_session, user, module, mc02, mode=SessionMode.EXAM,
             status=SessionStatus.CORRECTION_INCOMPLETE, score=9)  # jamais une réussite
    in_progress = _session(db_session, user, module, mc02, mode=SessionMode.PRACTICE,
                           status=SessionStatus.IN_PROGRESS)

    progress = user_uaa_progress(db_session, user)
    assert progress[mc01.id]["practice_done"] == 1
    assert progress[mc01.id]["exam_best"] == 0.6
    assert progress[mc02.id]["exam_best"] is None
    assert progress[mc02.id]["in_progress_session_id"] == in_progress.id

    html = authenticated_client.get("/modules/ampcr").text
    page = _text(html)
    assert "Entraîné ×1" in page
    assert "Examen blanc réussi (60\u00a0%)" in page
    assert f'href="/sessions/{in_progress.id}"' in html

    _choose(authenticated_client)
    dashboard = _text(authenticated_client.get("/mon-parcours").text)
    assert "Reprendre la session" in dashboard
    assert "Entraînés\u00a0: 1/2" in dashboard


def test_transversal_scope_session_counts_for_revision_course(db_session):
    content = _content(db_session)
    user = User(email="scope@example.test", password_hash="x")
    db_session.add(user)
    db_session.commit()
    module, (mc01, _mc02) = content["AMPCR"]
    mc38 = UAA(code="MC38", title="Révision", slug="t136-mc38", position=38,
               is_published=True, module_id=module.id)
    db_session.add(mc38)
    db_session.commit()
    _session(db_session, user, module, mc01, mode=SessionMode.EXAM,
             status=SessionStatus.COMPLETED, score=15, count=20, scope="mc38")
    progress = user_uaa_progress(db_session, user)
    assert progress[mc38.id]["exam_best"] == 0.75
    assert mc01.id not in progress


def test_module_path_only_offers_existing_spaces(client, db_session):
    _content(db_session)
    page = client.get("/modules/mb32").text
    assert 'href="/uaa/t136-uaa1"' in page
    assert 'href="/uaa/t136-uaa1/practice"' not in page  # aucun bloc d'entraînement
    assert 'href="/uaa/t136-uaa1/exam"' not in page
    assert "Connecte-toi" in page


def test_course_page_has_sequences_and_neighbours(client, db_session):
    _content(db_session)
    page = client.get("/uaa/t136-mc01").text
    assert 'id="jc-lesson"' in page
    assert "js/lesson_sequences.js" in page
    assert 'href="/uaa/t136-mc02"' in page  # cours suivant, sans verrou
    assert "J&#39;ai lu ce cours" in page or "J'ai lu ce cours" in page


def test_subject_pages_render_tiles(client, db_session):
    _content(db_session)
    assert "Informatique" in client.get("/subjects").text
    assert client.get("/subjects/informatique").status_code == 200


# --- Illustrations (aucun appel réseau) ----------------------------------------------------------


class _FakeImageProvider:
    def __init__(self, error=None):
        self.calls = 0
        self.error = error

    def generate_image(self, prompt, size, quality):
        import io

        from PIL import Image

        self.calls += 1
        if self.error:
            raise self.error
        buffer = io.BytesIO()
        Image.new("RGB", (1536, 1024), (120, 90, 200)).save(buffer, format="PNG")
        return buffer.getvalue()


def test_illustrations_are_cropped_webp_and_never_regenerated(tmp_path, monkeypatch):
    Image = pytest.importorskip("PIL.Image")  # outil manuel serveur, Pillow hors dépendances

    from app.v1 import parcours_images

    fake = _FakeImageProvider()
    monkeypatch.setattr(parcours_images, "get_image_provider", lambda: fake)
    assert parcours_images.generate(tmp_path, only={"accueil", "informatique"}) == 0
    assert Image.open(tmp_path / "informatique.webp").size == (960, 540)
    assert Image.open(tmp_path / "accueil.webp").size == (1200, 800)
    assert (tmp_path / "informatique.json").exists()
    assert parcours_images.generate(tmp_path, only={"accueil"}) == 0
    assert fake.calls == 2  # déjà présente : aucun nouvel appel


def test_quota_error_stops_generation_without_partial_file(tmp_path, monkeypatch):
    pytest.importorskip("PIL.Image")
    from app.ai.provider import AIResponseError
    from app.v1 import parcours_images

    fake = _FakeImageProvider(AIResponseError("statut 429 (code=insufficient_quota)"))
    monkeypatch.setattr(parcours_images, "get_image_provider", lambda: fake)
    assert parcours_images.generate(tmp_path) == 1
    assert fake.calls == 1  # arrêt immédiat, pas de boucle
    assert not list(tmp_path.glob("*.webp"))

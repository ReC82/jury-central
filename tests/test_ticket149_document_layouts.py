"""Ticket #149 — documents sources composés selon leur vraie nature.

Garanties vérifiées :
- chaque document FSE installé a une mise en page dédiée, liée au texte EXACT de sa version
  (empreinte) — un texte modifié retombe sur le rendu générique ;
- tout texte affiché est un extrait mot pour mot du document, et le contenu est couvert ;
- aucune mention éditoriale entre crochets, aucun renvoi de cours, aucune annotation-réponse
  retirée (`omitted`) n'apparaît à l'écran ;
- numéro réel réutilisé (« Document 3 »), fiches visées mises en avant ;
- rendu réel dans la session, la page document et les résultats.
"""

import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from markupsafe import escape

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA
from app.seed import seed
from app.templating import templates
from app.v1 import document_layouts as dl
from app.v1 import fse_bank
from app.v1.models import (
    Question,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    SourceDocumentVersion,
    User,
)


def _fse_documents() -> list[tuple[str, str]]:
    """(titre, texte) de chaque document créé par la banque FSE (mêmes constantes que le
    seed) — lu depuis les appels `create_source_document` de `app.v1.fse_bank`."""
    source = Path(fse_bank.__file__).read_text(encoding="utf-8")
    pairs = re.findall(r"title=([A-Z0-9_]+_TITLE),\s*content_text=([A-Z0-9_]+_TEXT)", source)
    documents = []
    for title_name, text_name in pairs:
        documents.append((getattr(fse_bank, title_name), getattr(fse_bank, text_name)))
    return documents


FSE_DOCUMENTS = _fse_documents()


def _doc(title, text, content_json=None, doc_id=1):
    return SimpleNamespace(id=doc_id, title=title, content_text=text, content_json=content_json)


def _render(doc, label="Document de référence", question_text=""):
    module = templates.env.get_template("_document_layouts.html").module
    return str(module.render(doc, label, question_text=question_text, uid="t"))


def test_every_fse_document_has_a_layout_bound_to_its_exact_text():
    assert len(FSE_DOCUMENTS) == 30
    registered = dl.registered_layouts()
    assert len(registered) == 30
    for title, text in FSE_DOCUMENTS:
        assert (title, dl.text_fingerprint(text)) in registered, title


def test_a_modified_text_falls_back_to_the_generic_rendering():
    title, text = FSE_DOCUMENTS[0]
    assert dl.resolve_layout(_doc(title, text)) is not None
    assert dl.resolve_layout(_doc(title, text + " Phrase ajoutée.")) is None
    html = _render(_doc(title, text + " Phrase ajoutée."))
    assert "jc-sd-prose" in html


@pytest.mark.parametrize("title,text", FSE_DOCUMENTS, ids=[t[:40] for t, _ in FSE_DOCUMENTS])
def test_layout_text_is_verbatim_and_covers_the_document(title, text):
    layout = dl.resolve_layout(_doc(title, text))
    corpus = dl.verification_corpus(title, text, layout)
    for fragment in dl.iter_content_strings(layout):
        assert dl.comparable(fragment) in corpus, fragment
    full = dl.comparable(f"{title} {text}")
    for fragment in layout.get("omitted", []):
        assert dl.comparable(fragment) in full, fragment
    # Couverture : les mots du corps du document (hors mention initiale entre crochets et
    # fragments volontairement retirés) sont presque tous affichés.
    body = "\n\n".join(dl.generic_parts(text)["paragraphs"])
    words = re.findall(r"\w{4,}", dl.verification_corpus("", body, layout))
    shown = " ".join(dl.comparable(s) for s in dl.iter_content_strings(layout))
    missing = [w for w in words if w not in shown]
    assert len(missing) <= 0.05 * len(words), sorted(set(missing))


@pytest.mark.parametrize("title,text", FSE_DOCUMENTS, ids=[t[:40] for t, _ in FSE_DOCUMENTS])
def test_rendered_document_has_no_editorial_brackets_course_refs_or_omitted_answers(title, text):
    layout = dl.resolve_layout(_doc(title, text))
    html = _render(_doc(title, text))
    assert f"jc-sd--{layout['kind']}" in html
    visible = re.sub(r"<[^>]+>", " ", html)
    assert "[" not in visible and "]" not in visible
    assert not re.search(r"voir FSE\d", visible)
    for fragment in layout.get("omitted", []):
        assert str(escape(fragment)) not in html


def test_answer_revealing_annotations_are_not_shown():
    by_title = dict(FSE_DOCUMENTS)
    budget = _render(_doc(fse_bank.FSE12_BUDGET_TITLE, by_title[fse_bank.FSE12_BUDGET_TITLE]))
    assert "1 100" not in budget and "déficit" not in budget
    aid = _render(_doc(fse_bank.FSE15_AID_TITLE, by_title[fse_bank.FSE15_AID_TITLE]))
    assert "flux monétaire" not in aid
    situations = _render(_doc(fse_bank.FSE09_SITUATIONS_TITLE, by_title[fse_bank.FSE09_SITUATIONS_TITLE]))
    assert "sans réponse unique trompeuse" not in situations


def test_real_document_number_is_reused_and_titles_numbered_documents_are_split():
    by_title = dict(FSE_DOCUMENTS)
    reactions = _doc(fse_bank.FSE16_REACTIONS_TITLE, by_title[fse_bank.FSE16_REACTIONS_TITLE])
    heading = dl.display_heading(reactions, dl.resolve_layout(reactions), "Document de référence")
    assert heading == {"label": "Document 3", "title": "Réactions des groupes concernés"}
    html = _render(reactions)
    assert "Témoignages fictifs — exercice pédagogique" in html
    assert html.count('class="jc-sd-quote ') == 3
    french = _doc("Document 1 — Le télétravail vu par la direction", "Texte.")
    assert dl.display_heading(french, None, "Document de référence") == {
        "label": "Document 1",
        "title": "Le télétravail vu par la direction",
    }
    other = _doc("Un article", "Texte.")
    assert dl.display_heading(other, None, "Document A")["label"] == "Document A"


def test_targeted_situations_are_put_forward_with_full_dossier_available():
    by_title = dict(FSE_DOCUMENTS)
    doc = _doc(fse_bank.FSE09_SITUATIONS_TITLE, by_title[fse_bank.FSE09_SITUATIONS_TITLE])
    layout = dl.resolve_layout(doc)
    question = (
        "Associe maintenant ces trois autres situations au bon niveau de pouvoir. "
        "Situation 5 (envoi de troupes) Situation 6 (normes environnementales territoriales) "
        "Situation 7 (campagne culturelle en bibliothèque)"
    )
    assert dl.focus_numbers(layout, question) == [5, 6, 7]
    assert dl.focus_numbers(layout, "Classe chaque situation selon le niveau de pouvoir.") == []
    html = _render(doc, question_text=question)
    assert "Concernés par cette question" in html
    assert "Voir tout le document (10 fiches)" in html
    assert "overflow-y" not in html and "max-height" not in html


def test_content_json_layout_is_rendered_directly_for_new_documents():
    layout = {
        "kind": "forum_post",
        "notice": "Document fictif — exercice pédagogique",
        "forum": "Forum test",
        "topic": "Sujet test",
        "pseudo": "pseudo_test",
        "status": "Utilisateur anonyme",
        "body": "Corps du message.",
    }
    doc = _doc("Nouveau document", "Corps du message.", content_json={"layout": layout})
    assert dl.resolve_layout(doc) is layout
    assert "jc-sd-forum-topic" in _render(doc)


def test_generic_rendering_keeps_exact_text_and_moves_leading_note_out_of_the_body():
    text = "[Document fictif, rédigé pour cet exercice]\n\nPremier paragraphe.\n\nSecond [cité] paragraphe."
    parts = dl.generic_parts(text)
    assert parts["notice"] == "Document fictif, rédigé pour cet exercice"
    assert parts["text"] == "Premier paragraphe.\n\nSecond [cité] paragraphe."
    html = _render(_doc("Texte libre", text))
    assert 'class="jc-sd-notice"' in html and "Second [cité] paragraphe." in html


# --- Rendu réel dans les pages ------------------------------------------------------------


def _fse16_question(db_session, prompt_start: str) -> Question:
    seed()
    uaa = db_session.query(UAA).filter_by(slug="fse-fse16").first()
    fse_bank.import_fse16_to_bank(db_session, uaa.module, uaa)
    db_session.commit()
    for question in db_session.query(Question).filter_by(uaa_id=uaa.id):
        if question.current_version.content_json.get("prompt", "").startswith(prompt_start):
            return question
    raise AssertionError(prompt_start)


def _single_question_session(db_session, question: Question, mode=SessionMode.EXAM) -> int:
    user = db_session.query(User).filter_by(email="eleve-test@example.test").first()
    session = QuestionnaireSession(
        user_id=user.id, mode=mode, module_id=question.module_id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(SessionQuestion(
        session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0,
    ))
    db_session.commit()
    return session.id


def test_exam_question_page_shows_composed_document_and_distinct_finish(authenticated_client, db_session):
    question = _fse16_question(db_session, "D'après le document 3")
    session_id = _single_question_session(db_session, question)
    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    assert response.status_code == 200
    html = response.text
    assert '<span class="jc-sd-label">Document 3</span>' in html
    assert "Réactions des groupes concernés" in html
    assert "[Réactions fictives" not in html
    assert 'class="jc-q-prompt"' in html
    assert "Terminer l&#39;évaluation" in html or "Terminer l'évaluation" in html
    assert 'jc-q-finish' in html
    assert html.count("Ouvrir en grand</a>") == 1


def test_document_page_and_results_use_the_same_component(authenticated_client, db_session, monkeypatch):
    question = _fse16_question(db_session, "D'après le document 3")
    doc_id = question.current_version.content_json["source_document_version_id"]
    page = authenticated_client.get(f"/documents/{doc_id}")
    assert page.status_code == 200
    assert "jc-sd--quotes" in page.text and "Ouvrir en grand</a>" not in page.text

    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    session_id = _single_question_session(db_session, question, mode=SessionMode.PRACTICE)
    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    token = re.search(r'name="csrf_token" value="([^"]+)"', response.text).group(1)
    authenticated_client.post(
        f"/sessions/{session_id}/answer",
        data={"csrf_token": token, "position": 1, "direction": "submit", "text": "La capacité du réseau."},
    )
    confirm = authenticated_client.get(f"/sessions/{session_id}/submit-confirm")
    token = re.search(r'name="csrf_token" value="([^"]+)"', confirm.text).group(1)
    authenticated_client.post(f"/sessions/{session_id}/submit", data={"csrf_token": token, "severity": "3"})
    from app.v1.session_service import claim_next_pending_correction_job, run_correction_job

    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=fake)
    results = authenticated_client.get(f"/sessions/{session_id}")
    assert results.status_code == 200
    assert "Revoir le document" in results.text
    assert "jc-sd--quotes" in results.text
    assert db_session.get(SourceDocumentVersion, doc_id) is not None

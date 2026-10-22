"""Ticket #86 — choisir le nombre de questions (10/20/30/40, 50 pour MC38/global AMPCR)
AVANT de démarrer un entraînement ou une évaluation.

Aucun appel OpenAI réel : `FakeAIProvider` (variante à numérotation continue pour que deux
lots successifs ne produisent jamais les mêmes énoncés factices).
"""

import re
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from app.ai.fake_provider import FakeAIProvider, _fake_question
from app.ai.provider import AIProviderError
from app.ai.schemas import Questionnaire
from app.models import UAA, Module
from app.seed import seed
from app.v1.bank import import_mc01_legacy_to_bank
from app.v1.mc38_transversal import MC38_SESSION_SCOPE
from app.v1.models import QuestionnaireSession, SessionBuildJob, SessionStatus
from app.v1.session_service import (
    GENERATION_BATCH_SIZE,
    REQUESTED_COUNT_KEY,
    _diversity_capped_oversample,
    claim_next_pending_build_job,
    run_session_build_job,
)


class _ContinuousFake(FakeAIProvider):
    """Comme `FakeAIProvider`, mais la numérotation des questions continue d'un appel à
    l'autre (sinon le lot 2 répète les énoncés du lot 1 et serait dédoublonné)."""

    def __init__(self, fail_after_calls: int | None = None):
        super().__init__()
        self._offset = 0
        self._fail_after_calls = fail_after_calls

    def generate_questionnaire(self, request):
        if self._fail_after_calls is not None and len(self.questionnaire_calls) >= self._fail_after_calls:
            self.questionnaire_calls.append(request)
            raise AIProviderError("panne simulée")
        self.questionnaire_calls.append(request)
        allowed = list(request.allowed_types)
        questions = []
        for i in range(request.question_count):
            index = self._offset + i
            questions.append(_fake_question(f"fake-q{index + 1}", allowed[index % len(allowed)], 1.0, index))
        self._offset += request.question_count
        return Questionnaire(mode=request.mode, questions=questions)


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _seed(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    return ampcr, mc01


def _login(client, email="t86@example.test"):
    token = _csrf(client.get("/register").text)
    client.post(
        "/register",
        data={
            "csrf_token": token, "email": email, "password": "test-password-1234",
            "password_confirm": "test-password-1234", "display_name": "T86",
        },
    )


def _start(client, path, **data):
    token = _csrf(client.get(path).text)
    return client.post(
        f"{path}/start", data={"csrf_token": token, "difficulty": "medium", **data}, follow_redirects=False
    )


def _build(db_session, provider) -> QuestionnaireSession:
    job = claim_next_pending_build_job(db_session)
    assert job is not None
    run_session_build_job(db_session, job=job, provider=provider)
    assert job.created_session_id is not None, job.error_message
    return db_session.get(QuestionnaireSession, job.created_session_id)


def _options(html: str) -> list[int]:
    return [int(v) for v in re.findall(r'name="question_count"\s+id="question-count-\d+"\s+value="(\d+)"', html)]


def _checked(html: str) -> int:
    match = re.search(r'value="(\d+)"\s+autocomplete="off"\s+checked', html)
    assert match
    return int(match.group(1))


@pytest.fixture
def generation_available(monkeypatch):
    monkeypatch.setattr("app.v1.session_service.settings.openai_api_key", "sk-test-not-used")


# --- Écran de démarrage -----------------------------------------------------------------------


def test_landing_offers_all_lengths_when_generation_is_available(client, db_session, generation_available):
    _seed(db_session)
    _login(client)

    practice = client.get("/uaa/ampcr-mc01/practice").text
    assert "Nombre de questions" in practice
    assert _options(practice) == [10, 20, 30, 40]
    assert _checked(practice) == 10
    assert "révision rapide" in practice and "examen approfondi" in practice

    exam = client.get("/uaa/ampcr-mc01/exam").text
    assert _options(exam) == [10, 20, 30, 40]
    assert _checked(exam) == 20
    assert "Commencer l'évaluation" in exam


def test_mc38_and_global_offer_50(client, db_session, generation_available):
    _seed(db_session)
    _login(client)
    assert _options(client.get("/uaa/ampcr-mc38/exam").text) == [10, 20, 30, 40, 50]
    assert _options(client.get("/modules/ampcr/exam").text) == [10, 20, 30, 40, 50]
    assert _options(client.get("/modules/ampcr/practice").text) == [10, 20, 30, 40, 50]


def test_landing_hides_lengths_the_bank_alone_cannot_satisfy(client, db_session):
    """Sans fournisseur IA configuré (cas des tests), seule la banque compte."""
    _seed(db_session)
    _login(client)
    html = client.get("/uaa/ampcr-mc01/exam").text
    options = _options(html)
    assert options and options[0] == 10
    assert 40 not in options
    assert _checked(html) == max(n for n in options if n <= 20)


# --- Création, persistance, progression ---------------------------------------------------------


@pytest.mark.parametrize("count", [10, 20, 30, 40])
def test_exam_session_has_chosen_length_without_duplicates(client, db_session, monkeypatch, count):
    _seed(db_session)
    fake = _ContinuousFake()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    _login(client)

    r = _start(client, "/uaa/ampcr-mc01/exam", question_count=str(count))
    assert r.status_code == 303
    assert db_session.query(SessionBuildJob).one().question_count == count

    session = _build(db_session, fake)
    assert session.question_count == count
    assert session.parameters_json[REQUESTED_COUNT_KEY] == count
    question_ids = [sq.question_version.question_id for sq in session.session_questions]
    version_ids = [sq.question_version_id for sq in session.session_questions]
    assert len(set(question_ids)) == count
    assert len(set(version_ids)) == count
    assert all(call.question_count <= GENERATION_BATCH_SIZE for call in fake.questionnaire_calls)

    # Compteur cohérent et reprise : la page de session affiche la taille choisie.
    page = client.get(f"/sessions/{session.id}").text
    assert f"Question 1 / {count}" in page
    assert client.get(f"/sessions/{session.id}").text.count(f"/ {count}") >= 1


def test_mc38_exam_of_50_questions(client, db_session, monkeypatch):
    _seed(db_session)
    fake = _ContinuousFake()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    _login(client)

    _start(client, "/uaa/ampcr-mc38/exam", question_count="50")
    session = _build(db_session, fake)
    assert session.question_count == 50
    assert len({sq.question_version.question_id for sq in session.session_questions}) == 50
    assert session.parameters_json["scope"] == MC38_SESSION_SCOPE
    # Plusieurs lots, chacun avec des contextes MC01→MC37 tirés à nouveau.
    assert len(fake.questionnaire_calls) >= 3


def test_invalid_lengths_are_rejected(client, db_session, monkeypatch):
    _seed(db_session)
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: _ContinuousFake())
    _login(client)
    assert _start(client, "/uaa/ampcr-mc01/practice", question_count="35").status_code == 400
    assert _start(client, "/uaa/ampcr-mc01/practice", question_count="abc").status_code == 400
    # 50 est réservé aux parcours couvrant tout le programme.
    assert _start(client, "/uaa/ampcr-mc01/exam", question_count="50").status_code == 400
    assert db_session.query(SessionBuildJob).count() == 0


def test_missing_field_keeps_historical_volume(client, db_session, monkeypatch):
    _seed(db_session)
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: _ContinuousFake())
    _login(client)
    _start(client, "/uaa/ampcr-mc01/exam")
    _start(client, "/uaa/ampcr-mc38/exam")
    counts = sorted(job.question_count for job in db_session.query(SessionBuildJob).all())
    assert counts == [10, 20]


def test_later_batch_failure_keeps_earlier_batches(client, db_session, monkeypatch):
    _seed(db_session)
    fake = _ContinuousFake(fail_after_calls=1)
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    _login(client)
    _start(client, "/uaa/ampcr-mc01/exam", question_count="40")
    session = _build(db_session, fake)
    ids = [sq.question_version.question_id for sq in session.session_questions]
    assert len(ids) == len(set(ids))
    assert session.question_count > GENERATION_BATCH_SIZE
    assert session.parameters_json[REQUESTED_COUNT_KEY] == 40


# --- Historique / export ------------------------------------------------------------------------


def test_history_and_export_show_requested_length(client, db_session, monkeypatch):
    _seed(db_session)
    fake = _ContinuousFake()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    _login(client)
    _start(client, "/uaa/ampcr-mc01/practice", question_count="20")
    session = _build(db_session, fake)

    # Simule une session plus courte que choisie, puis terminée.
    session.question_count = 18
    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.now(UTC)
    session.score = 0
    db_session.commit()

    assert "(sur 20 choisies)" in client.get("/mes-sessions").text
    export = client.get(f"/sessions/{session.id}/export.md")
    assert export.status_code == 200
    assert "- Nombre de questions : 18 (choisi : 20)" in export.text


# --- Diversité proportionnelle à la longueur ------------------------------------------------------


def _stub_pool(sizes: dict[str, int]):
    return [SimpleNamespace(key=key) for key, size in sizes.items() for _ in range(size)]


@pytest.mark.parametrize(
    ("target", "min_keys"), [(10, 3), (20, 4), (30, 6), (40, 6)]
)
def test_diversity_cap_grows_with_length(target, min_keys):
    pool = _stub_pool({"hardware": 80, "systems": 40, "networks": 40, "wifi": 40, "troubleshooting": 40, "pro": 40})
    capped = _diversity_capped_oversample(pool, target, lambda q: q.key)
    per_key = {}
    for q in capped:
        per_key[q.key] = per_key.get(q.key, 0) + 1
    cap = -(-target // min_keys)
    assert max(per_key.values()) <= cap
    # Un tirage de `target` questions dans ce pool couvre donc au moins `min_keys` valeurs.
    assert len(per_key) >= min_keys

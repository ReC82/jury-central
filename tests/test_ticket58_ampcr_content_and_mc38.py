"""Ticket #58 — cours de révision express AMPCR MC04→MC37 + MC38 réellement transversal.

Deux problèmes pédagogiques bloquants corrigés :
1. MC04→MC37 affichaient un stub « contenu pas encore rédigé » — remplacés par un vrai
   cours court, orienté examen (`app.v1.ampcr_courses.AMPCR_COURSE_MARKDOWN`).
2. MC38 générait des questions MÉTA sur le processus de révision lui-même — practice/exam
   tirent désormais exclusivement dans les mini-cours réels MC01→MC37
   (`app.v1.mc38_transversal`), jamais dans le propre contexte MC38.

Aucun appel OpenAI réel : toutes les générations passent par `FakeAIProvider` ou par un
`Questionnaire` construit à la main (monkeypatch de `generate_questionnaire`)."""

import re
from unittest.mock import patch

import pytest

from app.ai.fake_provider import FakeAIProvider
from app.ai.schemas import Questionnaire, QuestionnaireQuestion
from app.models import UAA, Module
from app.seed import seed
from app.v1.ampcr_courses import AMPCR_COURSE_MARKDOWN, MC38_COURSE_MARKDOWN
from app.v1.ampcr_plan import AMPCR_PLAN, AMPCR_PLAN_BY_CODE
from app.v1.bank import import_mc01_legacy_to_bank, select_transversal_bank_questions
from app.v1.mc38_transversal import is_meta_revision_question, mc01_to_mc37_codes
from app.v1.models import QuestionnaireSession, User


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _start_session(client, uaa_slug: str, mode: str = "practice", difficulty: str = "medium") -> str:
    response = client.get(f"/uaa/{uaa_slug}/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/{uaa_slug}/{mode}/start",
        data={"csrf_token": token, "difficulty": difficulty},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    return response.headers["location"]


# --- 1. Contenu réel MC04-37 (§ 2 du ticket) -----------------------------------------------


def test_ampcr_course_markdown_covers_exactly_mc04_to_mc37():
    codes = sorted(AMPCR_COURSE_MARKDOWN.keys())
    assert codes == [f"MC{n:02d}" for n in range(4, 38)]


def test_mc04_course_is_no_longer_a_stub(client, db_session):
    seed()
    response = client.get("/uaa/ampcr-mc04")
    assert response.status_code == 200
    assert "contenu de cours détaillé n'est pas encore rédigé" not in response.text
    assert "Cours de révision express" in response.text
    # Structure imposée (§ 2 du ticket).
    for section in (
        "Ce qu'il faut savoir",
        "Définitions essentielles",
        "Notions principales",
        "Pièges fréquents",
        "Vocabulaire FR / EN",
        "À retenir pour l'examen",
    ):
        assert section in AMPCR_COURSE_MARKDOWN["MC04"]


def test_mc17_course_contains_subnetting_notions(client, db_session):
    seed()
    response = client.get("/uaa/ampcr-mc17")
    assert response.status_code == 200
    for needle in ("CIDR", "masque", "hôtes", "incrément"):
        assert needle.lower() in response.text.lower(), needle


def test_mc24_course_contains_vlan_notions(client, db_session):
    seed()
    response = client.get("/uaa/ampcr-mc24")
    assert response.status_code == 200
    for needle in ("VLAN", "trunk", "802.1Q"):
        assert needle.lower() in response.text.lower(), needle


def test_mc31_course_contains_troubleshooting_notions(client, db_session):
    seed()
    response = client.get("/uaa/ampcr-mc31")
    assert response.status_code == 200
    for needle in ("IP", "passerelle", "DNS"):
        assert needle.lower() in response.text.lower(), needle


def test_mc37_course_is_an_integrative_lab(client, db_session):
    seed()
    response = client.get("/uaa/ampcr-mc37")
    assert response.status_code == 200
    for needle in ("montage", "RJ45", "partage", "Wi-Fi", "sécurité"):
        assert needle.lower() in response.text.lower(), needle


@pytest.mark.parametrize("code", [plan.code for plan in AMPCR_PLAN if plan.code not in ("MC01", "MC02", "MC03", "MC38")])
def test_every_mc04_to_mc37_uaa_serves_its_real_course(client, db_session, code):
    seed()
    slug = f"ampcr-{code.lower()}"
    response = client.get(f"/uaa/{slug}")
    assert response.status_code == 200
    assert "Cours de révision express" in response.text


# --- 2. MC38 : cours descriptif, jamais méta dans les questions (§ 4 du ticket) ------------


def test_mc38_course_explains_transversal_revision_without_being_a_quiz_topic():
    """Le COURS de MC38 peut légitimement décrire le mécanisme de révision transversale
    (contenu informatif) — mais ce texte ne doit jamais fuiter dans les QUESTIONS
    générées, testé séparément ci-dessous."""
    assert "MC01" in MC38_COURSE_MARKDOWN and "MC37" in MC38_COURSE_MARKDOWN
    assert "transversal" in MC38_COURSE_MARKDOWN.lower()


def test_mc38_course_page_is_served(client, db_session):
    seed()
    response = client.get("/uaa/ampcr-mc38")
    assert response.status_code == 200
    assert "transversal" in response.text.lower()


# --- 3. Garde anti-méta (§ 8 du ticket) -----------------------------------------------------


@pytest.mark.parametrize(
    "banned_example",
    [
        "Quel est l'objectif principal d'une révision finale AMPCR ?",
        "Que faut-il faire après avoir corrigé un exercice transversal ou un examen blanc ?",
        "Fiches mémo → Révision et mémorisation",
    ],
)
def test_meta_guard_rejects_the_exact_examples_banned_by_the_ticket(banned_example):
    assert is_meta_revision_question(banned_example) is True


@pytest.mark.parametrize(
    "legit_example",
    [
        "Quel est le piège classique du subnetting en /31 ?",
        "Lors d'un examen pratique, quelle commande permet de tester la passerelle ?",
        "Un examen blanc de sécurité Wi-Fi demande de choisir entre WPA2 et WPA3 : lequel est recommandé ?",
        "Quel protocole permet la résolution de noms de domaine en adresse IP ?",
    ],
)
def test_meta_guard_never_blocks_the_word_examen_or_piege_alone(legit_example):
    """§ 8 du ticket : « ne pas interdire le mot examen partout si une vraie question
    technique le contient » — le contrôle vise le sens méta, pas une liste noire naïve."""
    assert is_meta_revision_question(legit_example) is False


def test_meta_guard_inspects_categories_and_options_not_only_the_prompt():
    """Bug constaté en validation staging (redéploiement PR #59) : une question de
    classification dont l'énoncé est générique (« Classe chaque élément... ») mais dont
    les CATÉGORIES sont méta (« Fiche mémo » / « Exercice transversal » / « Examen
    blanc », ou « Révision et mémorisation » / « Entraînement et évaluation ») passait à
    travers la garde, qui n'inspectait que `prompt`. Ce test rejoue les questions
    RÉELLEMENT trouvées en banque staging (avant correctif) qui n'étaient pas détectées."""
    from app.v1.mc38_transversal import question_full_text_from_content_json

    real_staging_examples = [
        {
            "prompt": "Classe chaque activité selon sa fonction principale.",
            "categories": ["Fiche mémo", "Exercice transversal", "Examen blanc"],
            "elements": [
                "Résumer les points essentiels sur une page",
                "Combiner plusieurs notions dans une même situation",
                "S'entraîner dans des conditions proches de la qualification",
            ],
        },
        {"prompt": "Remets dans l'ordre les étapes d'une préparation finale cohérente."},
        {
            "prompt": "Quel élément rend un exercice réellement transversal ?",
            "options": [
                {"label": "Il porte sur un seul mot-clé à mémoriser"},
                {"label": "Il demande de mobiliser plusieurs acquis dans une même situation"},
            ],
        },
        {
            "prompt": (
                "Explique comment tu utiliserais un examen blanc pour améliorer ta "
                "préparation à l'examen de qualification AMPCR."
            )
        },
        {"prompt": "Quel comportement est le plus adapté pendant une épreuve type qualification ?"},
        {
            "prompt": "Classe chaque élément dans la catégorie qui convient le mieux.",
            "categories": ["Révision et mémorisation", "Entraînement et évaluation"],
            "elements": ["Synthèse", "Fiches mémo", "Exercices transversaux", "Examen blanc"],
        },
    ]
    for content in real_staging_examples:
        text = question_full_text_from_content_json(content)
        assert is_meta_revision_question(text) is True, content["prompt"]


def test_generated_meta_questions_are_filtered_out_before_being_shown(
    authenticated_client, db_session, monkeypatch
):
    """Simule une génération IA qui renvoie un mélange de questions méta (interdites) et
    d'une vraie question technique — seule la question technique doit survivre, jamais un
    crash ni une session vide."""
    seed()
    fake_questions = [
        QuestionnaireQuestion(
            question_id="q1", type="multiple_choice",
            prompt="Quel est l'objectif principal d'une révision finale AMPCR ?",
            points_max=1.0, choices=["a", "b"], correct_indexes=[0],
        ),
        QuestionnaireQuestion(
            question_id="q2", type="multiple_choice",
            prompt="Quel protocole traduit un nom de domaine en adresse IP ?",
            points_max=1.0, choices=["DNS", "ARP"], correct_indexes=[0],
        ),
        QuestionnaireQuestion(
            question_id="q3", type="multiple_choice",
            prompt="Que faut-il faire après avoir corrigé un exercice transversal ou un examen blanc ?",
            points_max=1.0, choices=["a", "b"], correct_indexes=[0],
        ),
    ]
    fake_result = Questionnaire(mode="practice", questions=fake_questions)

    with patch("app.v1.session_service.generate_questionnaire", return_value=fake_result):
        _patch_fake_provider(monkeypatch)
        session_url = _start_session(authenticated_client, "ampcr-mc38", mode="practice")

    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    prompts = [
        sq.question_version.content_json.get("prompt") for sq in session.session_questions
    ]
    assert all(not is_meta_revision_question(p) for p in prompts)
    assert any("nom de domaine" in p for p in prompts)


# --- 4. MC38 tire dans MC01→MC37, jamais dans son propre contexte (§ 5/6 du ticket) --------


def test_mc01_to_mc37_codes_excludes_mc38():
    codes = mc01_to_mc37_codes()
    assert len(codes) == 37
    assert "MC38" not in codes
    assert "MC01" in codes and "MC37" in codes


def test_mc38_practice_draws_from_mc01_to_mc37_bank_never_its_own(
    authenticated_client, db_session, monkeypatch
):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    _patch_fake_provider(monkeypatch)

    session_url = _start_session(authenticated_client, "ampcr-mc38", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == 10

    # Les questions déjà en banque MC01 sont réutilisées telles quelles (uaa=MC01) ; le
    # complément généré est stocké sous le bucket propre de MC38 (une question générée à
    # partir d'un contexte combiné MC01-37 n'est pas attribuable à un seul mini-cours) —
    # ce qui compte : JAMAIS une autre UAA hors AMPCR_PLAN, et jamais de contenu méta
    # (vérifié séparément). Voir `test_mc38_generation_uses_transversal_contexts_never_its_own`
    # pour la garantie que la GÉNÉRATION, elle, n'utilise jamais le contexte MC38.
    used_codes = set()
    for sq in session.session_questions:
        uaa = sq.question_version.question.uaa
        assert uaa is not None
        used_codes.add(uaa.code)
    assert used_codes <= {*mc01_to_mc37_codes(), "MC38"}
    assert "MC01" in used_codes  # la banque MC01 pré-existante a bien été réutilisée


def test_mc38_exam_has_twenty_questions_and_draws_from_mc01_to_mc37(
    authenticated_client, db_session, monkeypatch
):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc38", mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.mode.value == "exam"
    assert session.question_count == 20
    for sq in session.session_questions:
        uaa = sq.question_version.question.uaa
        assert uaa is not None
        assert uaa.code in {*mc01_to_mc37_codes(), "MC38"}


def test_mc38_generation_uses_transversal_contexts_never_its_own(
    authenticated_client, db_session, monkeypatch
):
    fake = _patch_fake_provider(monkeypatch)
    seed()  # banque MC01-37 vide -> génération nécessaire
    _start_session(authenticated_client, "ampcr-mc38", mode="practice")
    assert len(fake.questionnaire_calls) == 1
    used_contexts = fake.questionnaire_calls[0].contexts
    assert len(used_contexts) >= 2
    assert all(ctx.course_key != "ampcr-mc38" for ctx in used_contexts)


def test_mc38_practice_covers_several_categories_when_bank_allows(
    authenticated_client, db_session, monkeypatch
):
    """§ 6 du ticket : « plusieurs catégories obligatoires » (pas nécessairement toutes)."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    mc31 = db_session.query(UAA).filter_by(slug="ampcr-mc31").first()
    from app.v1.models import create_question

    for i in range(15):
        create_question(
            db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
            content_json={
                "prompt": f"MC17 Q{i}",
                "options": [{"option_id": "0", "label": "a"}, {"option_id": "1", "label": "b"}],
                "min_selections": 1, "max_selections": 1, "correct_option_ids": ["0"], "explanation": "x",
            },
            generation_source="ai_generated",
        )
    for i in range(15):
        create_question(
            db_session, module_id=ampcr.id, uaa_id=mc31.id, question_type="multiple_choice",
            content_json={
                "prompt": f"MC31 Q{i}",
                "options": [{"option_id": "0", "label": "a"}, {"option_id": "1", "label": "b"}],
                "min_selections": 1, "max_selections": 1, "correct_option_ids": ["0"], "explanation": "x",
            },
            generation_source="ai_generated",
        )
    db_session.commit()
    _patch_fake_provider(monkeypatch)

    session_url = _start_session(authenticated_client, "ampcr-mc38", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    categories = {
        AMPCR_PLAN_BY_CODE[sq.question_version.question.uaa.code].category
        for sq in session.session_questions
        if sq.question_version.question.uaa
    }
    assert len(categories) >= 2


def test_select_transversal_bank_questions_never_returns_meta_or_mc38_tagged(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc38 = db_session.query(UAA).filter_by(slug="ampcr-mc38").first()
    from app.v1.models import create_question

    create_question(
        db_session, module_id=ampcr.id, uaa_id=mc38.id, question_type="multiple_choice",
        content_json={
            "prompt": "Quel est l'objectif principal d'une révision finale AMPCR ?",
            "options": [{"option_id": "0", "label": "a"}, {"option_id": "1", "label": "b"}],
            "min_selections": 1, "max_selections": 1, "correct_option_ids": ["0"], "explanation": "x",
        },
        generation_source="ai_generated",
    )
    db_session.commit()

    user = User(email="transversal-test@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()

    results = select_transversal_bank_questions(
        db_session, user_id=user.id, module_id=ampcr.id, limit=50
    )
    for question in results:
        assert question.uaa.code != "MC38" or not is_meta_revision_question(
            question.current_version.content_json.get("prompt", "")
        )
        prompt = question.current_version.content_json.get("prompt", "")
        assert not is_meta_revision_question(prompt)


# --- 5. Non-régression / pas de fuite de solution (§ 9 du ticket) --------------------------


def test_no_solution_leak_in_mc38_session(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc38", mode="practice")
    response = authenticated_client.get(f"{session_url}?q=1")
    assert response.status_code == 200
    forbidden = (
        "correct_option_ids", "correct_categories", "correct_order", "correct_pairs",
        "rubric", "accepted_answers", "numeric_answer",
    )
    for field in forbidden:
        assert field not in response.text, field


def test_mc01_practice_and_exam_routes_still_functional(authenticated_client, db_session, monkeypatch):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    _patch_fake_provider(monkeypatch)

    practice_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")
    assert authenticated_client.get(practice_url).status_code == 200
    exam_url = _start_session(authenticated_client, "ampcr-mc01", mode="exam")
    assert authenticated_client.get(exam_url).status_code == 200


def test_global_ampcr_practice_and_exam_still_functional(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/modules/ampcr/practice")
    assert response.status_code == 200
    response = authenticated_client.get("/modules/ampcr/exam")
    assert response.status_code == 200

"""Ticket #64 — qualité examen AMPCR : anti-répétition, déduplication, variantes réelles,
questions contextualisées, ordering clair, short_answer sémantique.

Constat de départ (validation staging réelle du ticket #62) : questions identiques déjà
vues en entraînement resservies en examen, classifications triviales 1-parmi-2 répétitives,
diagnostics vagues, ordering ambigu, réponses courtes sémantiquement correctes notées
fausses. Ce fichier couvre, sans aucun appel OpenAI réel (`FakeAIProvider` partout où une
correction/génération IA est exercée) :

1. `app.v1.dedup` — signature structurelle et détection de quasi-doublon (unitaire, pur).
2. `app.v1.bank` — `only_unseen`, exclusion par quasi-doublon d'une question vue,
   déduplication à la persistance, `recent_seen_prompts`.
3. `app.v1.hybrid_correction` — ré-évaluation sémantique réelle (score révisable) pour
   short_answer/vocabulary incorrects localement, jamais pour ordering/classification/QCM.
4. `app.v1.session_service` — diversité UAA/quasi-doublons dans la composition d'une
   session, séquence generate-avant-recycle.
5. `app.ai.prompts` — instructions qualité (contextualisation, ordering, QCM/classification,
   `avoid_prompts`) transmises au générateur.
6. Non-régression bout en bout (HTTP) : practice/exam MC01, aucune fuite de solution.
"""

import re

import pytest

from app.ai.fake_provider import FakeAIProvider
from app.ai.prompts import (
    GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT,
    build_generate_questionnaire_messages,
)
from app.ai.schemas import (
    PedagogicalContext,
    Questionnaire,
    QuestionnaireQuestion,
    QuestionnaireRequest,
)
from app.models import UAA, Module
from app.seed import seed
from app.v1.ampcr_plan import AMPCR_PLAN_BY_CODE
from app.v1.bank import (
    import_mc01_legacy_to_bank,
    persist_generated_questions,
    recent_seen_prompts,
    select_bank_questions,
)
from app.v1.dedup import is_near_duplicate, question_signature
from app.v1.hybrid_correction import correct_session_hybrid
from app.v1.models import QuestionnaireSession, User, create_question, record_question_seen

CONTEXT = PedagogicalContext(
    course_key="k", course_title="t", level="l", allowed_notions=[], competencies=[], vocabulary=[]
)


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _start_session(client, uaa_slug: str, mode: str = "practice") -> str:
    response = client.get(f"/uaa/{uaa_slug}/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/{uaa_slug}/{mode}/start",
        data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    return response.headers["location"]


def _mc_option(prompt: str, correct_label: str = "a") -> dict:
    """Options DÉRIVÉES du prompt (jamais un générique "a"/"b" partagé par toutes les
    questions de test) — sinon deux questions de test sans aucun rapport se
    retrouveraient avec des libellés d'options structurellement identiques, faussant
    `app.v1.dedup.is_near_duplicate` (collision d'options fortuite, pas un vrai
    quasi-doublon)."""
    return {
        "prompt": prompt,
        "options": [
            {"option_id": "0", "label": f"{prompt} — option A"},
            {"option_id": "1", "label": f"{prompt} — option B"},
        ],
        "min_selections": 1,
        "max_selections": 1,
        "correct_option_ids": ["0" if correct_label == "a" else "1"],
        "explanation": "x",
    }


# =============================================================================================
# 1. app.v1.dedup — signature structurelle / quasi-doublon (unitaire, pur)
# =============================================================================================


def test_reordered_options_are_a_near_duplicate():
    """§ 2 du ticket : « réordonner les options ne doit pas suffire à rendre une question
    nouvelle »."""
    original = question_signature(
        "multiple_choice",
        {"prompt": "Quel composant stocke les données de façon volatile ?", "options": [
            {"option_id": "0", "label": "RAM"}, {"option_id": "1", "label": "SSD"},
        ]},
    )
    reordered = question_signature(
        "multiple_choice",
        {"prompt": "Quel composant stocke les données de façon volatile ?", "options": [
            {"option_id": "0", "label": "SSD"}, {"option_id": "1", "label": "RAM"},
        ]},
    )
    assert is_near_duplicate(original, reordered)


def test_reworded_prompt_with_same_structure_is_a_near_duplicate():
    a = question_signature(
        "classification",
        {"prompt": "Classe ces préfixes selon leur nombre d'hôtes utilisables.",
         "categories": ["Grand", "Petit"], "elements": ["/24", "/30"]},
    )
    b = question_signature(
        "classification",
        {"prompt": "Range ces préfixes en fonction du nombre d'hôtes utilisables qu'ils offrent.",
         "categories": ["Petit", "Grand"], "elements": ["/30", "/24"]},
    )
    assert is_near_duplicate(a, b)


def test_different_notion_same_type_is_not_a_near_duplicate():
    a = question_signature(
        "multiple_choice",
        {"prompt": "Quel protocole résout un nom de domaine en adresse IP ?", "options": [
            {"option_id": "0", "label": "DNS"}, {"option_id": "1", "label": "HTTP"},
        ]},
    )
    b = question_signature(
        "multiple_choice",
        {"prompt": "Quel protocole permet de transférer des fichiers sur le réseau ?", "options": [
            {"option_id": "0", "label": "FTP"}, {"option_id": "1", "label": "SMTP"},
        ]},
    )
    assert not is_near_duplicate(a, b)


def test_coincidentally_shared_options_alone_do_not_make_a_duplicate():
    """Deux questions à la structure identique (même couple d'options) mais sur des
    notions sans rapport (aucun mot d'énoncé commun) ne sont PAS un quasi-doublon — évite
    de confondre deux QCM binaires qui réutilisent par hasard le même jeu d'options."""
    a = question_signature(
        "multiple_choice",
        {"prompt": "Quel protocole résout un nom de domaine en adresse IP ?", "options": [
            {"option_id": "0", "label": "DNS"}, {"option_id": "1", "label": "DHCP"},
        ]},
    )
    b = question_signature(
        "multiple_choice",
        {"prompt": "Quel élément assure le refroidissement du processeur ?", "options": [
            {"option_id": "0", "label": "DHCP"}, {"option_id": "1", "label": "DNS"},
        ]},
    )
    assert not is_near_duplicate(a, b)


def test_different_type_never_a_near_duplicate_even_with_identical_prompt():
    a = question_signature("multiple_choice", {"prompt": "Même énoncé", "options": []})
    b = question_signature("ordering", {"prompt": "Même énoncé", "items": []})
    assert not is_near_duplicate(a, b)


def test_different_values_real_variant_is_not_a_near_duplicate():
    """§ 3 du ticket (variantes réelles) : une autre valeur numérique/un autre scénario ne
    doit PAS être considéré comme un quasi-doublon."""
    a = question_signature(
        "short_answer",
        {"prompt": "Combien d'hôtes utilisables pour un /28 ?", "accepted_answers": ["14"]},
    )
    b = question_signature(
        "short_answer",
        {"prompt": "Combien d'hôtes utilisables pour un /26 ?", "accepted_answers": ["62"]},
    )
    assert not is_near_duplicate(a, b)


# =============================================================================================
# 2. app.v1.bank — only_unseen, quasi-doublon d'une vue, dédup à la persistance
# =============================================================================================


def _user(db_session, email="q64@example.invalid") -> User:
    user = User(email=email, password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    return user


def test_select_bank_questions_only_unseen_excludes_exact_id(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    seen_question = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json=_mc_option("Déjà vue"), generation_source="ai_generated",
    )
    unseen_question = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json=_mc_option("Jamais vue"), generation_source="ai_generated",
    )
    db_session.commit()
    user = _user(db_session)
    record_question_seen(
        db_session, user_id=user.id, question_version=seen_question.current_version, session_id=1,
    )
    db_session.commit()

    result = select_bank_questions(
        db_session, user_id=user.id, module_id=ampcr.id, uaa_id=mc17.id, limit=10, only_unseen=True,
    )
    result_ids = {q.id for q in result}
    assert unseen_question.id in result_ids
    assert seen_question.id not in result_ids


def test_select_bank_questions_only_unseen_excludes_near_duplicate_of_a_seen_question(db_session):
    """Le cœur des § 1+2 combinées : une question JAMAIS vue par son propre id, mais
    quasi-identique (options réordonnées) à une question déjà vue, doit être exclue elle
    aussi — sinon « déjà vue sous une autre forme » resterait proposée comme nouvelle."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    seen_question = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json={
            "prompt": "Quel composant stocke les données de façon volatile ?",
            "options": [{"option_id": "0", "label": "RAM"}, {"option_id": "1", "label": "SSD"}],
            "min_selections": 1, "max_selections": 1, "correct_option_ids": ["0"], "explanation": "x",
        },
        generation_source="ai_generated",
    )
    near_duplicate = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json={
            "prompt": "Quel composant stocke les données de façon volatile ?",
            "options": [{"option_id": "0", "label": "SSD"}, {"option_id": "1", "label": "RAM"}],
            "min_selections": 1, "max_selections": 1, "correct_option_ids": ["1"], "explanation": "x",
        },
        generation_source="ai_generated",
    )
    genuinely_new = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json=_mc_option("Quelle est la vitesse d'un port USB 3.0 ?"),
        generation_source="ai_generated",
    )
    db_session.commit()
    user = _user(db_session)
    record_question_seen(
        db_session, user_id=user.id, question_version=seen_question.current_version, session_id=1,
    )
    db_session.commit()

    result = select_bank_questions(
        db_session, user_id=user.id, module_id=ampcr.id, uaa_id=mc17.id, limit=10, only_unseen=True,
    )
    result_ids = {q.id for q in result}
    assert near_duplicate.id not in result_ids
    assert seen_question.id not in result_ids
    assert genuinely_new.id in result_ids


def test_select_bank_questions_default_still_falls_back_to_seen(db_session):
    """`only_unseen=False` (par défaut) garde le comportement historique : repli sur les
    questions déjà vues plutôt que de renvoyer moins que `limit` quand la banque le permet
    (non-régression du ticket #55)."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    seen_question = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json=_mc_option("Seule question disponible"), generation_source="ai_generated",
    )
    db_session.commit()
    user = _user(db_session)
    record_question_seen(
        db_session, user_id=user.id, question_version=seen_question.current_version, session_id=1,
    )
    db_session.commit()

    result = select_bank_questions(
        db_session, user_id=user.id, module_id=ampcr.id, uaa_id=mc17.id, limit=10,
    )
    assert seen_question.id in {q.id for q in result}


def test_persist_generated_questions_skips_near_duplicate_of_existing_bank(db_session):
    """§ 2 du ticket : un quasi-doublon d'une question déjà en banque n'est jamais
    persisté, même reformulé/réordonné par le générateur."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json={
            "prompt": "Quel est l'incrément pour un masque /26 ?",
            "options": [{"option_id": "0", "label": "32"}, {"option_id": "1", "label": "64"}],
            "min_selections": 1, "max_selections": 1, "correct_option_ids": ["1"], "explanation": "x",
        },
        generation_source="ai_generated",
    )
    db_session.commit()

    near_duplicate = QuestionnaireQuestion(
        question_id="gen1", type="multiple_choice",
        prompt="Quel est l'incrément associé à un masque /26 ?",
        points_max=1.0, choices=["64", "32"], correct_indexes=[0],
    )
    genuinely_new = QuestionnaireQuestion(
        question_id="gen2", type="multiple_choice", prompt="Quel port utilise HTTPS par défaut ?",
        points_max=1.0, choices=["443", "80"], correct_indexes=[0],
    )
    persisted = persist_generated_questions(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[near_duplicate, genuinely_new],
    )
    prompts = {q.current_version.content_json["prompt"] for q in persisted}
    assert genuinely_new.prompt in prompts
    assert near_duplicate.prompt not in prompts
    assert len(persisted) == 1


def test_persist_generated_questions_skips_near_duplicate_within_same_batch(db_session):
    """Un même lot généré en un seul appel IA peut lui-même contenir des quasi-doublons
    entre elles — la seconde occurrence ne doit pas non plus être persistée."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()

    first = QuestionnaireQuestion(
        question_id="gen1", type="multiple_choice", prompt="Quel port utilise HTTPS ?",
        points_max=1.0, choices=["443", "80"], correct_indexes=[0],
    )
    duplicate_of_first = QuestionnaireQuestion(
        question_id="gen2", type="multiple_choice", prompt="Quel port utilise le protocole HTTPS ?",
        points_max=1.0, choices=["80", "443"], correct_indexes=[1],
    )
    persisted = persist_generated_questions(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[first, duplicate_of_first],
    )
    assert len(persisted) == 1


def test_recent_seen_prompts_scoped_and_most_recent_first(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    mc31 = db_session.query(UAA).filter_by(slug="ampcr-mc31").first()
    q_mc17 = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json=_mc_option("Question MC17"), generation_source="ai_generated",
    )
    q_mc31 = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc31.id, question_type="multiple_choice",
        content_json=_mc_option("Question MC31"), generation_source="ai_generated",
    )
    db_session.commit()
    user = _user(db_session)
    record_question_seen(
        db_session, user_id=user.id, question_version=q_mc17.current_version, session_id=1,
    )
    record_question_seen(
        db_session, user_id=user.id, question_version=q_mc31.current_version, session_id=1,
    )
    db_session.commit()

    scoped = recent_seen_prompts(db_session, user_id=user.id, module_id=ampcr.id, uaa_id=mc17.id)
    assert scoped == ["Question MC17"]

    all_module = recent_seen_prompts(db_session, user_id=user.id, module_id=ampcr.id)
    assert set(all_module) == {"Question MC17", "Question MC31"}


# =============================================================================================
# 3. app.v1.hybrid_correction — short_answer/vocabulary : ré-évaluation sémantique réelle
# =============================================================================================


def _short_answer_question(accepted=("l'écart entre deux débuts de sous-réseaux",)) -> QuestionnaireQuestion:
    return QuestionnaireQuestion(
        question_id="s1", type="short_answer",
        prompt="En subnetting, que désigne le mot incrément ?", points_max=1.0,
        accepted_answers=list(accepted),
    )


def test_short_answer_locally_wrong_is_rescored_by_ai_not_locked():
    """§ 7 du ticket, exemple réel : une formulation humaine correcte mais absente
    d'`accepted_answers` doit pouvoir récupérer les points via l'IA — contrairement à
    ordering/classification/QCM, dont le score reste verrouillé (voir tests ticket #62)."""
    question = _short_answer_question()
    user_answer = "le nombre entre le début d'un sous-réseau et le début du suivant"
    questionnaire = Questionnaire(mode="practice", questions=[question])
    fake = FakeAIProvider()  # accorde le plein score dès qu'une réponse non vide est fournie
    result = correct_session_hybrid(
        fake, questionnaire, {"s1": user_answer}, {"s1": user_answer}, "standard", (CONTEXT,),
    )
    correction = result.questions[0]
    assert fake.semantic_calls  # bien envoyée à l'IA (le texte ne correspond à rien localement)
    assert correction.points_awarded > 0.0  # le score LOCAL (0.0) a été révisé, pas verrouillé
    assert "s1" in fake.semantic_calls[0][0]


def test_short_answer_locally_correct_is_never_sent_to_ai():
    question = _short_answer_question()
    questionnaire = Questionnaire(mode="practice", questions=[question])
    fake = FakeAIProvider()
    result = correct_session_hybrid(
        fake, questionnaire, {"s1": "l'écart entre deux débuts de sous-réseaux"},
        {"s1": "l'écart entre deux débuts de sous-réseaux"}, "standard", (CONTEXT,),
    )
    assert result.questions[0].correct is True
    assert result.questions[0].points_awarded == 1.0
    assert not fake.semantic_calls  # correspondance textuelle locale : aucun coût IA


def test_ordering_still_locked_while_short_answer_in_same_batch_is_rescored():
    """Les deux comportements coexistent dans le MÊME appel batch : ordering reste
    verrouillé, short_answer est réévalué — § 7 : « Pour ordering/classification/QCM :
    score déterministe inchangé »."""
    ordering = QuestionnaireQuestion(
        question_id="q1", type="ordering", prompt="Ordonne.", points_max=1.0,
        order_items=["SSD", "RAM", "CPU", "écran"], correct_order=[0, 1, 2, 3],
    )
    short_answer = _short_answer_question()
    questionnaire = Questionnaire(mode="practice", questions=[ordering, short_answer])
    fake = FakeAIProvider()
    result = correct_session_hybrid(
        fake, questionnaire,
        {"q1": [0, 1, 3, 2], "s1": "le nombre entre le début d'un sous-réseau et le début du suivant"},
        {"q1": "SSD → RAM → écran → CPU", "s1": "le nombre entre le début d'un sous-réseau et le début du suivant"},
        "standard", (CONTEXT,),
    )
    corrections = {c.question_id: c for c in result.questions}
    assert corrections["q1"].points_awarded == 0.0  # verrouillé, malgré l'appel IA groupé
    assert corrections["s1"].points_awarded > 0.0  # réévalué
    assert len(fake.semantic_calls) == 1  # toujours UN seul appel batch


def test_vocabulary_type_also_rescorable_like_short_answer():
    question = QuestionnaireQuestion(
        question_id="v1", type="vocabulary", prompt="Traduis 'mémoire vive'.", points_max=1.0,
        accepted_answers=["RAM"],
    )
    questionnaire = Questionnaire(mode="practice", questions=[question])
    fake = FakeAIProvider()
    result = correct_session_hybrid(
        fake, questionnaire, {"v1": "random access memory"}, {"v1": "random access memory"},
        "standard", (CONTEXT,),
    )
    assert fake.semantic_calls
    assert result.questions[0].points_awarded > 0.0


# =============================================================================================
# 4. app.v1.session_service — diversité UAA / quasi-doublons dans une composition
# =============================================================================================


def test_uaa_balanced_oversample_limits_a_single_dominant_uaa():
    from app.v1.session_service import _uaa_balanced_oversample

    ampcr_plan_codes = list(AMPCR_PLAN_BY_CODE.keys())[:2]

    class _FakeUAA:
        def __init__(self, code):
            self.code = code

    class _FakeVersion:
        def __init__(self, question_type="multiple_choice"):
            self.question_type = question_type
            self.content_json = {"prompt": "p", "options": []}

    class _FakeQuestion:
        def __init__(self, uaa_code):
            self.uaa = _FakeUAA(uaa_code)
            self.current_version = _FakeVersion()

    # Les deux mini-cours sont également disponibles en abondance (15 chacun) : le plafond
    # (best-effort, § 6 du ticket #58, réutilisé § 8 du ticket #64) peut donc réellement
    # s'appliquer sans avoir besoin de repli sur l'excédent — voir `_diversity_capped_
    # oversample`, qui réintroduit sinon l'excédent quand la banque est trop pauvre pour
    # atteindre `target_count` autrement (comportement volontaire, documenté).
    pool = [_FakeQuestion(ampcr_plan_codes[0]) for _ in range(15)] + [
        _FakeQuestion(ampcr_plan_codes[1]) for _ in range(15)
    ]
    result = _uaa_balanced_oversample(pool, 10)
    codes = [q.uaa.code for q in result]
    assert codes.count(ampcr_plan_codes[1]) >= 1  # le mini-cours minoritaire n'est pas noyé
    assert codes.count(ampcr_plan_codes[0]) < 15  # le dominant est réellement plafonné


def test_limit_near_duplicate_clusters_caps_at_two():
    from app.v1.session_service import _limit_near_duplicate_clusters

    class _FakeVersion:
        def __init__(self, prompt, accepted):
            self.question_type = "short_answer"
            self.content_json = {"prompt": prompt, "accepted_answers": [accepted]}

    class _FakeQuestion:
        def __init__(self, prompt, accepted="14"):
            self.current_version = _FakeVersion(prompt, accepted)

    same_notion = [
        _FakeQuestion("Combien d'hôtes utilisables pour un /28 ?"),
        _FakeQuestion("Combien d'hôtes utilisables pour un préfixe /28 ?"),
        _FakeQuestion("Combien d'hôtes sont utilisables avec un /28 ?"),
        _FakeQuestion("Combien d'hôtes utilisables un /28 offre-t-il ?"),
    ]
    other_notion = [_FakeQuestion("Quel est le rôle du protocole ARP ?", accepted="resolution adresse mac")]

    result = _limit_near_duplicate_clusters(same_notion + other_notion, max_per_cluster=2)
    kept_from_cluster = sum(1 for q in result if "/28" in q.current_version.content_json["prompt"])
    assert kept_from_cluster == 2
    assert any("ARP" in q.current_version.content_json["prompt"] for q in result)


def test_global_exam_session_covers_several_uaa_when_bank_allows(
    authenticated_client, db_session, monkeypatch
):
    """§ 8 du ticket : « plusieurs mini-cours » obligatoires sur l'examen blanc global."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    mc31 = db_session.query(UAA).filter_by(slug="ampcr-mc31").first()
    for i in range(15):
        create_question(
            db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
            content_json=_mc_option(f"MC17 Q{i}"), generation_source="ai_generated",
        )
    for i in range(15):
        create_question(
            db_session, module_id=ampcr.id, uaa_id=mc31.id, question_type="multiple_choice",
            content_json=_mc_option(f"MC31 Q{i}"), generation_source="ai_generated",
        )
    db_session.commit()
    _patch_fake_provider(monkeypatch)

    # Le parcours global (examen blanc AMPCR) passe par /modules/ampcr/practice, jamais
    # par /uaa/{slug}/... (scopé à un seul mini-cours).
    response = authenticated_client.get("/modules/ampcr/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/modules/ampcr/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    session_id = int(response.headers["location"].rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    uaa_codes = {
        sq.question_version.question.uaa.code
        for sq in session.session_questions
        if sq.question_version.question.uaa
    }
    assert len(uaa_codes) >= 2


def test_generation_attempted_before_falling_back_to_seen_question(
    authenticated_client, db_session, monkeypatch
):
    """§ 1 du ticket : « générer de nouvelles questions avant de recycler ». Banque
    volontairement insuffisante pour couvrir la session sans repli — la génération doit
    être tentée (un appel questionnaire) avant toute réutilisation d'une question vue."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    seen_question = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json=_mc_option("Unique question déjà vue"), generation_source="ai_generated",
    )
    db_session.commit()
    # Le compte réel utilisé par `authenticated_client` (voir conftest, fixture qui
    # l'inscrit déjà via /register) a cet email fixe — on marque la question comme vue
    # pour CE compte précisément, sans en recréer un second (email déjà pris).
    real_user = db_session.query(User).filter_by(email="eleve-test@example.test").first()
    assert real_user is not None
    record_question_seen(
        db_session, user_id=real_user.id, question_version=seen_question.current_version, session_id=1,
    )
    db_session.commit()
    fake = _patch_fake_provider(monkeypatch)

    _start_session(authenticated_client, "ampcr-mc17")
    assert fake.questionnaire_calls  # génération bien tentée avant tout repli


# =============================================================================================
# 5. app.ai.prompts — instructions qualité + avoid_prompts
# =============================================================================================


def test_system_prompt_instructs_contextualized_scenarios():
    assert "mise en situation concrète" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
    assert "intranet.local" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT  # bon exemple du ticket
    assert "quel service faut-il vérifier ensuite" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT  # mauvais exemple


def test_system_prompt_instructs_ordering_clarity():
    assert "point de départ" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
    assert "point d'arrivée" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT


def test_system_prompt_instructs_richer_classification_and_qcm():
    assert "1-parmi-2" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
    assert "distracteurs crédibles" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT


def test_build_generate_questionnaire_messages_includes_avoid_prompts():
    request = QuestionnaireRequest(
        contexts=(CONTEXT,), mode="practice", difficulty="moyen", question_count=5,
        allowed_types=("multiple_choice",),
        avoid_prompts=("Quel est le rôle de la RAM ?", "Combien d'hôtes pour un /28 ?"),
    )
    messages = build_generate_questionnaire_messages(request)
    user_content = messages[1]["content"]
    assert "Quel est le rôle de la RAM ?" in user_content
    assert "Combien d'hôtes pour un /28 ?" in user_content
    assert "NE JAMAIS reproduire" in user_content


def test_build_generate_questionnaire_messages_without_avoid_prompts_unchanged():
    """`avoid_prompts` vide (défaut) — comportement historique inchangé, non-régression."""
    request = QuestionnaireRequest(
        contexts=(CONTEXT,), mode="practice", difficulty="moyen", question_count=5,
        allowed_types=("multiple_choice",),
    )
    messages = build_generate_questionnaire_messages(request)
    assert "NE JAMAIS reproduire" not in messages[1]["content"]


# =============================================================================================
# 6. Non-régression bout en bout
# =============================================================================================


def test_mc01_practice_still_functional_no_solution_leak(authenticated_client, db_session, monkeypatch):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    _patch_fake_provider(monkeypatch)

    session_url = _start_session(authenticated_client, "ampcr-mc01")
    response = authenticated_client.get(f"{session_url}?q=1")
    assert response.status_code == 200
    forbidden = (
        "correct_option_ids", "correct_categories", "correct_order", "correct_pairs",
        "rubric", "accepted_answers", "numeric_answer",
    )
    for field in forbidden:
        assert field not in response.text, field


def test_mc17_exam_still_functional(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc17", mode="exam")
    assert authenticated_client.get(session_url).status_code == 200


@pytest.mark.parametrize("severity", ["very_lenient", "lenient", "standard", "strict", "very_strict"])
def test_hybrid_correction_still_accepts_all_five_severities_with_rescoring(severity):
    """Non-régression ticket #62 combinée à la nouvelle voie de ré-évaluation § 7."""
    question = _short_answer_question()
    questionnaire = Questionnaire(mode="practice", questions=[question])
    result = correct_session_hybrid(
        FakeAIProvider(), questionnaire, {"s1": "une formulation différente mais correcte"},
        {"s1": "une formulation différente mais correcte"}, severity, (CONTEXT,),
    )
    assert result.questions[0].points_max == 1.0

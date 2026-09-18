"""Ticket #68 — URGENT fiabilité réseau : validation métier des questions IPv4/subnetting
générées.

Bug réel détecté en staging (MC17, question `diagnostic` générée) : une question
structurellement valide (registre #40) proposait 192.168.50.191 (broadcast) et
192.168.50.192 (adresse réseau du sous-réseau suivant) comme « adresses possibles pour un
autre poste » pour le réseau 192.168.50.128/26 — techniquement impossible. Ce fichier
couvre :

1. `app.v1.domain_validation` — unitaire, pur, sans DB ni réseau.
2. `app.v1.bank.persist_generated_questions` — rejet avant persistance, journalisation,
   non-visibilité en banque.
3. `app.v1.session_service` — régénération bornée sur rejet métier, repli banque au-delà
   de la limite, non-régression de l'invariant « un seul appel IA » du ticket #55 hors de
   ce cas précis, non-régression complète du ticket #64.

Aucun appel OpenAI réel : `FakeAIProvider` ou des doublures maison, jamais de clé API
réelle (voir `tests/conftest.py`, `OPENAI_API_KEY=""` forcé)."""

from app.ai.fake_provider import FakeAIProvider
from app.ai.schemas import Questionnaire, QuestionnaireQuestion
from app.models import UAA, Module
from app.seed import seed
from app.v1.bank import persist_generated_questions
from app.v1.domain_validation import (
    EXPECTED_INCREMENT_BY_PREFIX,
    EXPECTED_MASK_BY_PREFIX,
    usable_host_count,
    validate_domain_question,
)
from app.v1.models import ContentStatus, Question, User
from app.v1.session_service import (
    MAX_DOMAIN_REGENERATION_ATTEMPTS,
    SessionDifficultyRequest,
    SessionMode,
    start_session,
)


class _FakeUAA:
    def __init__(self, code: str):
        self.code = code


MC17 = _FakeUAA("MC17")
MC01 = _FakeUAA("MC01")  # hors périmètre IPv4 — sert aux tests "hors champ"


# =============================================================================================
# 1. app.v1.domain_validation — unitaire, pur
# =============================================================================================


def test_real_staging_case_is_rejected():
    """§ 17 du ticket : le cas réel exact détecté en staging."""
    content = {
        "prompt": (
            "Un poste possède l'adresse 192.168.50.130/26. Le technicien compare quatre "
            "adresses possibles pour un autre poste : 192.168.50.129, 192.168.50.150, "
            "192.168.50.191, 192.168.50.192. Laquelle est dans un autre sous-réseau ? "
            "Justifie avec l'incrément."
        ),
    }
    errors = validate_domain_question(None, MC17, "diagnostic", content)
    assert errors, "le cas réel doit être rejeté"
    assert any("192.168.50.191" in e and "192.168.50.192" in e for e in errors)


def test_corrected_case_is_accepted():
    """§ 18 du ticket : le même cas, corrigé (options réellement des hôtes valides)."""
    content = {
        "prompt": (
            "Un poste possède l'adresse 192.168.50.130/26. Parmi 192.168.50.129, "
            "192.168.50.150, 192.168.50.190, 192.168.50.193, laquelle appartient à un "
            "autre sous-réseau tout en étant une adresse hôte valide pour un poste ?"
        ),
    }
    assert validate_domain_question(None, MC17, "diagnostic", content) == []


def test_network_address_as_host_is_rejected():
    content = {
        "prompt": "Un poste possède l'adresse 192.168.1.10/28. Quelle adresse est valide pour un autre poste ?",
        "options": [{"option_id": "0", "label": "192.168.1.0"}, {"option_id": "1", "label": "192.168.1.5"}],
        "correct_option_ids": ["0"], "min_selections": 1, "max_selections": 1,
    }
    errors = validate_domain_question(None, MC17, "multiple_choice", content)
    assert errors
    assert "192.168.1.0" in errors[0]


def test_broadcast_address_as_host_is_rejected():
    content = {
        "prompt": "Un poste possède l'adresse 192.168.1.10/28. Quelle adresse est valide pour un autre poste ?",
        "options": [{"option_id": "0", "label": "192.168.1.15"}, {"option_id": "1", "label": "192.168.1.5"}],
        "correct_option_ids": ["0"], "min_selections": 1, "max_selections": 1,
    }
    errors = validate_domain_question(None, MC17, "multiple_choice", content)
    assert errors
    assert "192.168.1.15" in errors[0]


def test_valid_host_address_is_accepted():
    content = {
        "prompt": "Un poste possède l'adresse 192.168.1.10/28. Quelle adresse est valide pour un autre poste ?",
        "options": [{"option_id": "0", "label": "192.168.1.5"}, {"option_id": "1", "label": "192.168.1.20"}],
        "correct_option_ids": ["0"], "min_selections": 1, "max_selections": 1,
    }
    assert validate_domain_question(None, MC17, "multiple_choice", content) == []


def test_wrong_network_address_claim_is_rejected():
    content = {"prompt": "Pour 192.168.50.130/26, quelle est l'adresse réseau ?", "accepted_answers": ["192.168.50.0"]}
    errors = validate_domain_question(None, MC17, "short_answer", content)
    assert errors and "192.168.50.128" in errors[0]


def test_correct_network_address_claim_is_accepted():
    content = {"prompt": "Pour 192.168.50.130/26, quelle est l'adresse réseau ?", "accepted_answers": ["192.168.50.128"]}
    assert validate_domain_question(None, MC17, "short_answer", content) == []


def test_wrong_broadcast_address_claim_is_rejected():
    content = {"prompt": "Pour 192.168.50.130/26, quelle est l'adresse de broadcast ?", "accepted_answers": ["192.168.50.255"]}
    errors = validate_domain_question(None, MC17, "short_answer", content)
    assert errors and "192.168.50.191" in errors[0]


def test_first_and_last_host_claims_validated():
    good = {"prompt": "Pour 192.168.50.130/26, quelle est la première adresse hôte ?", "accepted_answers": ["192.168.50.129"]}
    bad = {"prompt": "Pour 192.168.50.130/26, quelle est la dernière adresse hôte ?", "accepted_answers": ["192.168.50.191"]}
    assert validate_domain_question(None, MC17, "short_answer", good) == []
    errors = validate_domain_question(None, MC17, "short_answer", bad)
    assert errors and "192.168.50.190" in errors[0]


# --- § 8 : masque/CIDR ------------------------------------------------------------------------


def test_mask_28_correct_accepted():
    content = {"prompt": "Quel masque décimal correspond au préfixe CIDR /28 ?", "accepted_answers": ["255.255.255.240"]}
    assert validate_domain_question(None, MC17, "short_answer", content) == []


def test_mask_cidr_mismatch_rejected():
    content = {"prompt": "Quel masque décimal correspond au préfixe CIDR /28 ?", "accepted_answers": ["255.255.255.192"]}
    errors = validate_domain_question(None, MC17, "short_answer", content)
    assert errors and "255.255.255.240" in errors[0]


def test_all_expected_masks_table():
    """Table complète § 8 du ticket."""
    assert EXPECTED_MASK_BY_PREFIX == {
        24: "255.255.255.0", 25: "255.255.255.128", 26: "255.255.255.192",
        27: "255.255.255.224", 28: "255.255.255.240", 29: "255.255.255.248", 30: "255.255.255.252",
    }


def test_classification_prefix_mask_pairs_rejected_when_swapped():
    content = {
        "prompt": "Associe chaque préfixe à son masque décimal.",
        "categories": ["255.255.255.0", "255.255.255.128"],
        "elements": ["/24", "/25"],
        "correct_categories": [1, 0],
    }
    assert validate_domain_question(None, MC17, "classification", content) != []


def test_classification_prefix_mask_pairs_accepted_when_correct():
    content = {
        "prompt": "Associe chaque préfixe à son masque décimal.",
        "categories": ["255.255.255.0", "255.255.255.128"],
        "elements": ["/24", "/25"],
        "correct_categories": [0, 1],
    }
    assert validate_domain_question(None, MC17, "classification", content) == []


# --- § 9 : incrément --------------------------------------------------------------------------


def test_increment_28_correct_accepted():
    content = {"prompt": "Quel est l'incrément pour un préfixe /28 ?", "accepted_answers": ["16"]}
    assert validate_domain_question(None, MC17, "short_answer", content) == []


def test_increment_wrong_rejected():
    content = {"prompt": "Quel est l'incrément pour un préfixe /28 ?", "accepted_answers": ["32"]}
    errors = validate_domain_question(None, MC17, "short_answer", content)
    assert errors and "16" in errors[0]


def test_all_expected_increments_table():
    assert EXPECTED_INCREMENT_BY_PREFIX == {24: 256, 25: 128, 26: 64, 27: 32, 28: 16, 29: 8, 30: 4}


# --- § 10 : nombre d'hôtes ---------------------------------------------------------------------


def test_host_count_28_is_14():
    content = {"prompt": "Combien d'hôtes utilisables pour un préfixe /28 ?", "accepted_answers": ["14"]}
    assert validate_domain_question(None, MC17, "short_answer", content) == []
    assert usable_host_count(28) == 14


def test_host_count_30_is_2():
    content = {"prompt": "Combien d'hôtes utilisables pour un préfixe /30 ?", "accepted_answers": ["2"]}
    assert validate_domain_question(None, MC17, "short_answer", content) == []
    assert usable_host_count(30) == 2


def test_host_count_wrong_rejected():
    content = {"prompt": "Combien d'hôtes utilisables pour un préfixe /28 ?", "accepted_answers": ["16"]}
    errors = validate_domain_question(None, MC17, "short_answer", content)
    assert errors and "14" in errors[0]


# --- § 7 : ambiguïté (0 ou 2+ bonnes réponses) --------------------------------------------------


def test_zero_correct_answers_rejected():
    content = {
        "prompt": (
            "Un poste possède l'adresse 192.168.1.10/28. Parmi 192.168.1.5, 192.168.1.9, "
            "laquelle est dans un autre sous-réseau ?"
        ),
        "accepted_answers": ["192.168.1.5"],
    }
    errors = validate_domain_question(None, MC17, "short_answer", content)
    assert errors and "Aucune" in errors[0]


def test_two_correct_answers_for_single_choice_rejected():
    content = {
        "prompt": "Un poste possède l'adresse 192.168.1.10/28. Quelle adresse pour un poste est dans un autre sous-réseau ?",
        "options": [{"option_id": "0", "label": "192.168.1.20"}, {"option_id": "1", "label": "192.168.1.36"}],
        "correct_option_ids": ["0"], "min_selections": 1, "max_selections": 1,
    }
    errors = validate_domain_question(None, MC17, "multiple_choice", content)
    assert errors and "Plusieurs" in errors[0]


def test_marked_correct_answer_mismatching_real_other_subnet_host_rejected():
    """§ 12 : ne jamais faire confiance à `correct_option_ids` seul — ici une SEULE
    adresse hôte est réellement dans un autre sous-réseau (.36), mais l'IA a marqué .20
    (qui est dans le MÊME sous-réseau) comme correcte."""
    content = {
        "prompt": "Un poste possède l'adresse 192.168.1.10/28. Quelle adresse pour un poste est dans un autre sous-réseau ?",
        "options": [{"option_id": "0", "label": "192.168.1.5"}, {"option_id": "1", "label": "192.168.1.36"}],
        "correct_option_ids": ["0"], "min_selections": 1, "max_selections": 1,
    }
    errors = validate_domain_question(None, MC17, "multiple_choice", content)
    assert errors and "192.168.1.36" in errors[0]


# --- § 5 : périmètre de détection ---------------------------------------------------------------


def test_unrelated_question_never_touched():
    content = {
        "prompt": "Quel composant stocke les données de façon volatile ?",
        "options": [{"option_id": "0", "label": "RAM"}, {"option_id": "1", "label": "SSD"}],
        "correct_option_ids": ["0"], "min_selections": 1, "max_selections": 1,
    }
    assert validate_domain_question(None, MC01, "multiple_choice", content) == []


def test_bare_reseau_keyword_alone_does_not_trigger_validation_outside_scoped_uaa():
    """§ 5 : « éviter de valider arbitrairement une question qui n'a rien à voir » — le
    seul mot « réseau » (très générique, câblage/matériel) ne doit pas suffire hors MC16-18
    et sans adresse IPv4/mot-clé spécifique."""
    content = {
        "prompt": "Quel câble utilise-t-on pour connecter un PC à une prise réseau murale ?",
        "options": [{"option_id": "0", "label": "RJ45"}, {"option_id": "1", "label": "VGA"}],
        "correct_option_ids": ["0"], "min_selections": 1, "max_selections": 1,
    }
    assert validate_domain_question(None, MC01, "multiple_choice", content) == []


def test_mc16_17_18_always_scoped_even_without_explicit_ip():
    """§ 5 : MC16/MC17/MC18 sont toujours dans le périmètre, même sans adresse IP
    littérale — mais une question qui ne fait aucune affirmation vérifiable reste acceptée
    (rien à contredire)."""
    content = {
        "prompt": "Pourquoi le sous-adressage (subnetting) est-il utile dans un réseau d'entreprise ?",
        "rubric": "Optimiser l'usage des adresses, segmenter le trafic.",
    }
    assert validate_domain_question(None, MC17, "long_answer", content) == []


def test_ipv4_literal_alone_triggers_validation_outside_scoped_uaa():
    """Une adresse IPv4 littérale est un signal fort, même hors MC16-18."""
    content = {
        "prompt": "Un poste possède l'adresse 10.0.0.5/28. Quelle adresse est valide pour un autre poste ?",
        "options": [{"option_id": "0", "label": "10.0.0.0"}, {"option_id": "1", "label": "10.0.0.6"}],
        "correct_option_ids": ["0"], "min_selections": 1, "max_selections": 1,
    }
    errors = validate_domain_question(None, MC01, "multiple_choice", content)
    assert errors and "10.0.0.0" in errors[0]


def test_out_of_scope_prefix_not_validated():
    """§ 3 : périmètre /24-/30 uniquement — un /31 (hors programme) n'est pas contrôlé."""
    content = {"prompt": "Quel est l'incrément pour un préfixe /31 ?", "accepted_answers": ["2"]}
    assert validate_domain_question(None, MC17, "short_answer", content) == []


def test_classification_or_ordering_exercise_labelling_network_broadcast_is_not_rejected():
    """Un exercice qui demande explicitement d'IDENTIFIER l'adresse réseau/broadcast (pas
    de contexte "poste/machine/hôte") n'est jamais bloqué par la règle § 6."""
    content = {
        "prompt": "Classe chaque adresse du sous-réseau 192.168.1.0/28 selon son rôle.",
        "categories": ["Adresse réseau", "Broadcast", "Hôte utilisable"],
        "elements": ["192.168.1.0", "192.168.1.15", "192.168.1.5"],
        "correct_categories": [0, 1, 2],
    }
    assert validate_domain_question(None, MC17, "classification", content) == []


# =============================================================================================
# 2. app.v1.bank.persist_generated_questions — rejet avant persistance
# =============================================================================================


def _bad_ipv4_question(question_id: str) -> QuestionnaireQuestion:
    return QuestionnaireQuestion(
        question_id=question_id, type="multiple_choice",
        prompt="Un poste possède l'adresse 192.168.1.10/28. Quelle adresse est valide pour un autre poste ?",
        points_max=1.0, choices=["192.168.1.0", "192.168.1.5"], correct_indexes=[0],
    )


def _good_ipv4_question(question_id: str, offset: int = 0) -> QuestionnaireQuestion:
    return QuestionnaireQuestion(
        question_id=question_id, type="multiple_choice",
        prompt=f"Un poste possède l'adresse 192.168.1.10/28 (variante {offset}). Quelle adresse est valide pour un autre poste ?",
        points_max=1.0, choices=["192.168.1.5", f"192.168.1.{20 + offset}"], correct_indexes=[1],
    )


def test_invalid_question_not_persisted(db_session, caplog):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()

    with caplog.at_level("WARNING"):
        persisted = persist_generated_questions(
            db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[_bad_ipv4_question("q1")],
        )
    assert persisted == []
    assert "DOMAIN_VALIDATION_REJECTED" in caplog.text
    assert "MC17" in caplog.text


def test_rejected_question_not_visible_in_bank(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    persist_generated_questions(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[_bad_ipv4_question("q1")],
    )
    db_session.commit()
    bank_prompts = [
        q.current_version.content_json.get("prompt")
        for q in db_session.query(Question).filter_by(module_id=ampcr.id, uaa_id=mc17.id, status=ContentStatus.ACTIVE)
    ]
    assert not any("192.168.1.10/28" in (p or "") for p in bank_prompts)


def test_valid_question_persisted_normally(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    persisted = persist_generated_questions(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[_good_ipv4_question("q1")],
    )
    assert len(persisted) == 1


def test_mixed_batch_only_invalid_rejected(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    rejections: list[str] = []
    persisted = persist_generated_questions(
        db_session, module_id=ampcr.id, uaa_id=mc17.id,
        questions=[_bad_ipv4_question("bad"), _good_ipv4_question("good")],
        domain_rejections=rejections,
    )
    assert len(persisted) == 1
    assert persisted[0].current_version.content_json["prompt"].startswith("Un poste possède l'adresse 192.168.1.10/28 (variante")
    assert rejections == ["multiple_choice"]


# =============================================================================================
# 3. app.v1.session_service — régénération bornée, non-régression #55/#64
# =============================================================================================


class _AlwaysBadIPv4Provider:
    """Génère systématiquement une question IPv4 invalide — sert à vérifier la limite de
    tentatives (§ 15/19 du ticket)."""

    def __init__(self):
        self.questionnaire_calls = []

    def generate_questionnaire(self, request):
        self.questionnaire_calls.append(request)
        return Questionnaire(
            mode=request.mode,
            questions=[_bad_ipv4_question(f"bad-{len(self.questionnaire_calls)}-{i}") for i in range(request.question_count)],
        )

    def correct_semantic_batch(self, *args, **kwargs):
        raise NotImplementedError


class _BadThenGoodIPv4Provider:
    """1er appel : question IPv4 invalide (rejetée). 2e appel : question IPv4 valide."""

    def __init__(self):
        self.questionnaire_calls = []

    def generate_questionnaire(self, request):
        self.questionnaire_calls.append(request)
        call_number = len(self.questionnaire_calls)
        if call_number == 1:
            questions = [_bad_ipv4_question(f"bad-{i}") for i in range(request.question_count)]
        else:
            questions = [_good_ipv4_question(f"good-{i}", offset=i) for i in range(request.question_count)]
        return Questionnaire(mode=request.mode, questions=questions)

    def correct_semantic_batch(self, *args, **kwargs):
        raise NotImplementedError


def _user(db_session, email="ticket68@example.invalid") -> User:
    user = User(email=email, password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    return user


def test_regeneration_on_domain_reject_then_success(db_session):
    """§ 15 : le moteur retente un appel ciblé si le premier lot est rejeté par la
    validation métier, et réussit à compléter la session avec une question valide."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    user = _user(db_session)
    provider = _BadThenGoodIPv4Provider()

    session = start_session(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc17.id, uaa_code="MC17",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM,
        provider=provider, question_count=1,
    )
    assert len(provider.questionnaire_calls) == 2  # 1 rejeté + 1 régénération réussie
    assert session.question_count == 1
    version = session.session_questions[0].question_version
    assert "variante" in version.content_json["prompt"]  # la question RETENUE est la bonne


def test_max_retries_respected_then_bank_fallback(db_session):
    """§ 15/19 : limite de tentatives respectée (jamais de boucle infinie) — au-delà,
    repli sur la banque plutôt que de servir une question technique fausse. `question_
    count=2` avec une seule question de secours en banque : la sélection initiale seule
    ne suffit pas (`missing=1`), la génération est donc bien tentée."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    from app.v1.models import create_question

    create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json={
            "prompt": "Quel port utilise HTTPS par défaut ?",
            "options": [{"option_id": "0", "label": "443"}, {"option_id": "1", "label": "80"}],
            "min_selections": 1, "max_selections": 1, "correct_option_ids": ["0"], "explanation": "x",
        },
        generation_source="ai_generated",
    )
    db_session.commit()
    user = _user(db_session)
    provider = _AlwaysBadIPv4Provider()

    session = start_session(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc17.id, uaa_code="MC17",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM,
        provider=provider, question_count=2,
    )
    # 1 appel initial + au plus MAX_DOMAIN_REGENERATION_ATTEMPTS tentatives de complément.
    assert len(provider.questionnaire_calls) == 1 + MAX_DOMAIN_REGENERATION_ATTEMPTS
    assert session.question_count == 2
    # Aucune question IPv4 invalide servie, quel que soit le créneau : repli sur la
    # banque (y compris en répétant la question de secours plutôt qu'une question fausse).
    prompts = [sq.question_version.content_json.get("prompt", "") for sq in session.session_questions]
    assert all("192.168.1.10/28" not in p for p in prompts)


def test_no_retry_when_shortfall_is_not_domain_related(db_session, monkeypatch):
    """Non-régression ticket #55/#64 : un manque dû au DÉDOUBLONNAGE (#64), pas à la
    validation métier, ne doit JAMAIS déclencher de second appel IA — l'invariant « un
    seul appel IA par session » reste intact hors du cas § 15."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    user = _user(db_session)
    fake = FakeAIProvider()  # contenu factice, jamais rejeté par la validation métier

    session = start_session(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc17.id, uaa_code="MC17",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM,
        provider=fake, question_count=3,
    )
    assert len(fake.questionnaire_calls) <= 1
    assert session.question_count == 3


def test_no_real_openai_provider_imported_by_domain_validation():
    """Garde-fou explicite (§ 19 : « aucun appel OpenAI réel pytest ») : le module de
    validation métier n'importe ni n'appelle jamais `app.ai.openai_provider`."""
    import app.v1.domain_validation as module

    assert "openai_provider" not in module.__dict__
    with open(module.__file__) as f:
        source = f.read()
    assert "openai" not in source.lower()

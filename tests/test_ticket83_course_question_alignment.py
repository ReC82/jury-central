"""Ticket #83 — alignement pédagogique cours ↔ questions : une question ne peut demander
une connaissance (ici, la signification d'un acronyme) que si elle est réellement
enseignée dans le cours du MC concerné ou dans le lexique AMPCR transverse (#84).

Cas réel ayant motivé le ticket : « Que signifie l'acronyme SMART ? » posée alors que
MC04 utilisait SMART sans jamais donner son développé.
"""

from app.v1.ampcr_courses import AMPCR_COURSE_MARKDOWN
from app.v1.ampcr_plan import AMPCR_PLAN_BY_CODE, _detailed_context
from app.v1.course_coverage import (
    check_course_coverage_gap,
    defined_notions_for_code,
)
from app.v1.quality_validation import QUALITY_VALIDATORS, validate_question_quality


class _FakeUaa:
    def __init__(self, code: str):
        self.code = code


# --- § 83.C : contenu MC04 enrichi -----------------------------------------------------------


def test_mc04_smart_acronym_is_expanded_in_course_content():
    text = AMPCR_COURSE_MARKDOWN["MC04"]
    assert "Self-Monitoring, Analysis and Reporting Technology" in text


def test_mc04_smart_expansion_explains_it_never_guarantees_or_replaces_backup():
    text = AMPCR_COURSE_MARKDOWN["MC04"]
    assert "jamais une garantie" in text
    assert "jamais une sauvegarde" in text or "remplace jamais\n  une sauvegarde" in text


# --- § 83.A : extraction structurelle des notions expliquées --------------------------------


def test_defined_notions_extraction_catches_bold_paren_pattern():
    notions = defined_notions_for_code("MC04")
    assert "SMART" in notions
    assert "TBW" in notions
    assert "SSD" in notions
    assert "HDD" in notions


def test_defined_notions_extraction_catches_bold_colon_pattern():
    # MC13 explique "**Modèle OSI** : 7 couches..." (deux-points, pas de parenthèse).
    notions = defined_notions_for_code("MC13")
    assert "OSI" in notions


def test_defined_notions_for_unknown_code_never_crashes():
    """`code=None`/inconnu : jamais d'exception — seules les notions du lexique
    transverse (#84 § F) s'appliquent alors, puisqu'aucun cours propre n'existe."""
    from app.v1.lexicon import lexicon_defined_notions

    assert defined_notions_for_code(None) == lexicon_defined_notions()
    assert defined_notions_for_code("MC99") == lexicon_defined_notions()


# --- § 83.B : garde serveur ------------------------------------------------------------------


def test_course_coverage_gap_rejects_undefined_acronym_question():
    uaa = _FakeUaa("MC04")
    content = {"prompt": "Que signifie l'acronyme ZXQW dans ce contexte ?"}
    errors = check_course_coverage_gap(None, uaa, "short_answer", content)
    assert len(errors) == 1
    assert "COURSE_COVERAGE_GAP" in errors[0]
    assert "ZXQW" in errors[0]


def test_course_coverage_gap_accepts_smart_now_taught_in_mc04():
    uaa = _FakeUaa("MC04")
    content = {"prompt": "Que signifie l'acronyme SMART pour un disque dur ou un SSD ?"}
    assert check_course_coverage_gap(None, uaa, "short_answer", content) == []


def test_course_content_alone_never_expands_cpu_on_mc01():
    """CPU/GPU ne sont expandés nulle part dans le texte de cours AMPCR (audit § 83.A) —
    preuve du gap réel trouvé par l'audit, indépendamment du lexique. Le pipeline complet
    (`check_course_coverage_gap`, qui consulte AUSSI le lexique § 84 F) reste testé
    séparément dans `tests/test_ticket84_ampcr_lexicon.py::
    test_lexicon_closes_the_cpu_gap_found_in_ticket_83_audit` — cette garde a fermé le
    gap exactement comme prévu, donc la question redevient acceptée en pratique."""
    from app.v1.course_coverage import _DEFINED_NOTIONS_BY_CODE

    assert "CPU" not in _DEFINED_NOTIONS_BY_CODE.get("MC01", frozenset())


def test_course_coverage_gap_ignores_prompts_without_acronym_question_pattern():
    uaa = _FakeUaa("MC04")
    content = {"prompt": "Quel type de connecteur relie un SSD SATA à la carte mère ?"}
    assert check_course_coverage_gap(None, uaa, "short_answer", content) == []


def test_course_coverage_gap_applies_regardless_of_question_type():
    """Contrairement à `validate_question_quality_rules` (§ 69, restreint à certains
    types), cette garde s'applique à TOUS les types — vocabulary/true_false compris."""
    uaa = _FakeUaa("MC04")
    content = {"prompt": "Que veut dire ZXQW ?"}
    for question_type in ("vocabulary", "true_false", "multiple_choice", "short_answer"):
        errors = check_course_coverage_gap(None, uaa, question_type, content)
        assert len(errors) == 1, question_type


def test_course_coverage_gap_skips_when_uaa_has_no_code():
    """Question sans rattachement MC (ex. transversale) : seul le lexique s'applique ; pas
    de faux rejet massif faute de MC identifiable."""
    content = {"prompt": "Que signifie l'acronyme ZXQW ?"}
    errors = check_course_coverage_gap(None, None, "short_answer", content)
    assert len(errors) == 1
    assert "(sans MC)" in errors[0]


def test_always_allowed_pc_never_flagged():
    uaa = _FakeUaa("MC29")
    content = {"prompt": "Que signifie PC dans ce contexte ?"}
    assert check_course_coverage_gap(None, uaa, "short_answer", content) == []


# --- Câblage dans le registre partagé ---------------------------------------------------------


def test_check_course_coverage_gap_registered_in_quality_validators():
    assert check_course_coverage_gap in QUALITY_VALIDATORS


def test_validate_question_quality_entry_point_rejects_course_coverage_gap():
    uaa = _FakeUaa("MC04")
    content = {"prompt": "Que représente l'acronyme ZXQW ?"}
    errors = validate_question_quality(None, uaa, "short_answer", content)
    assert any("COURSE_COVERAGE_GAP" in e for e in errors)


# --- § 83.B : allowed_notions/vocabulary enrichis pour le prompt de génération --------------


def test_ampcr_context_vocabulary_includes_real_course_notions():
    ctx = _detailed_context(AMPCR_PLAN_BY_CODE["MC04"])
    assert "SMART" in ctx.vocabulary
    assert "SSD" in ctx.vocabulary
    assert "HDD" in ctx.vocabulary


def test_ampcr_context_constraints_instructs_never_ask_undefined_acronym():
    ctx = _detailed_context(AMPCR_PLAN_BY_CODE["MC04"])
    assert "ne demande JAMAIS la signification" in ctx.constraints

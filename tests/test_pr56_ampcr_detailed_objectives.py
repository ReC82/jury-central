"""Correctif de revue PR #56 (ticket #55) : MC04→MC38 utilisaient uniquement leur titre
comme `allowed_notions`, jugé insuffisant par la revue ChatGPT pour borner fiablement la
génération avant l'examen. Ce module vérifie que chaque mini-cours du plan AMPCR expose
désormais son objectif pédagogique EXACT (transmis verbatim par ChatGPT, jamais inventé
par Claude) dans son `PedagogicalContext`, sans rien changer au fonctionnement du reste
du ticket #55."""

from app.ai.context import PEDAGOGICAL_CONTEXTS
from app.ai.schemas import PedagogicalContext
from app.v1.ampcr_plan import _OBJECTIVES_BY_CODE, AMPCR_CONTEXTS, AMPCR_PLAN


def _full_text(context: PedagogicalContext) -> str:
    return " ".join(
        [
            context.course_title,
            *context.allowed_notions,
            *context.competencies,
            *context.vocabulary,
            context.constraints,
        ]
    )


def test_objectives_dict_covers_exactly_the_38_plan_codes():
    codes = {plan.code for plan in AMPCR_PLAN}
    assert set(_OBJECTIVES_BY_CODE) == codes


def test_every_mc_context_has_title_and_non_trivial_notions():
    for plan in AMPCR_PLAN:
        context = AMPCR_CONTEXTS[plan.course_key]
        assert context.course_title
        assert context.allowed_notions, plan.code
        # Ne se limite plus au seul titre (ancien comportement corrigé par la PR #56).
        assert len(" ".join(context.allowed_notions)) > len(plan.title), plan.code


def test_mc04_to_mc38_expose_their_exact_plan_objective():
    # MC01-03 gardent leur cahier des charges existant, à la formulation différente de
    # l'objectif court du plan (autorisé explicitement : "peuvent conserver leur contexte
    # existant plus riche") — seuls MC04-38 doivent matcher l'objectif verbatim.
    for plan in AMPCR_PLAN:
        if plan.has_authored_content:
            continue
        context = AMPCR_CONTEXTS[plan.course_key]
        assert _OBJECTIVES_BY_CODE[plan.code] in _full_text(context), plan.code


def test_mc01_to_mc03_keep_their_existing_richer_context_untouched():
    for code in ("mc01", "mc02", "mc03"):
        key = f"ampcr-{code}"
        assert AMPCR_CONTEXTS[key] is PEDAGOGICAL_CONTEXTS[key]


def test_mc04_context_contains_storage_notions():
    text = _full_text(AMPCR_CONTEXTS["ampcr-mc04"]).lower()
    for needle in ("hdd", "ssd", "nvme", "smart", "sauvegarde"):
        assert needle in text, needle


def test_mc17_context_contains_subnetting_notions():
    text = _full_text(AMPCR_CONTEXTS["ampcr-mc17"]).lower()
    for needle in ("cidr", "masques", "hôtes"):
        assert needle in text, needle


def test_mc24_context_contains_vlan_notions():
    text = _full_text(AMPCR_CONTEXTS["ampcr-mc24"]).lower()
    for needle in ("vlan", "trunk", "802.1q"):
        assert needle in text, needle


def test_mc31_context_contains_troubleshooting_notions():
    text = _full_text(AMPCR_CONTEXTS["ampcr-mc31"]).lower()
    for needle in ("ip", "passerelle", "dns", "diagnostic"):
        assert needle in text, needle


def test_mc38_context_contains_final_revision_notions():
    text = _full_text(AMPCR_CONTEXTS["ampcr-mc38"]).lower()
    for needle in ("synthèse", "exercices transversaux", "examen"):
        assert needle in text, needle


def test_no_context_is_empty_for_any_of_the_38_mc():
    for plan in AMPCR_PLAN:
        context = AMPCR_CONTEXTS[plan.course_key]
        assert _full_text(context).strip()

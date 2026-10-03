"""Ticket #131 — audit de couverture pédagogique FSE01-17 (reprise du ticket #102).

Un seul gap réel trouvé en comparant le contenu réellement installé (pas les titres, pas
les anciens rapports, pas seulement les tests passants) au cahier des charges officiel
(issues GitHub #96-#101) : FSE10 n'expliquait jamais la notion d'**abstention**, alors que
le cahier des charges demande explicitement d'« expliquer blanc/nul/procuration sans
confondre abstention et vote blanc ». Absente de la théorie, des définitions, des pièges,
de la fiche mémo et de la banque de questions. Ce fichier verrouille le correctif.

La matrice complète (tous les cours, toutes les exigences, statut et justification) est
publiée dans docs/claude-reports/2026-10-03_ticket-131-fse-coverage-matrix.md — ce fichier
ne re-teste que le gap trouvé et corrigé, pas l'ensemble de la matrice (qui relève de la
lecture humaine du rapport, pas d'assertions automatisées)."""

from app.content import render_markdown
from app.v1.fse10_course import fse10_course_sections


def _sections_by_title():
    return dict(fse10_course_sections())


def test_abstention_defined_in_theory_and_definitions():
    html = render_markdown(_sections_by_title()["FSE10 — Théorie : notions et définitions"])
    assert "abstention" in html.lower()
    assert "<strong>Abstention</strong>" in html or "Abstention" in html


def test_abstention_distinguished_from_vote_blanc_explicitly():
    """Une simple mention ne suffit pas : vérifie que la distinction elle-même (pas
    seulement le mot) est explicite dans le texte visible."""
    html = render_markdown(_sections_by_title()["FSE10 — Théorie : notions et définitions"])
    text = html.lower()
    assert "ne pas se présenter" in text or "ne s'étant pas présenté" in text
    assert "vote blanc" in text and "abstention" in text


def test_abstention_piege_and_bonne_mauvaise_reponse_present():
    html = render_markdown(_sections_by_title()["FSE10 — Comparer pour ne pas confondre"])
    assert "abstention" in html.lower()
    # le piège dédié (converti en citation/WarningCard) et la paire mauvaise/bonne réponse
    assert "jc-compare" in html or "<blockquote>" in html


def test_abstention_in_fiche_memo():
    html = render_markdown(_sections_by_title()["FSE10 — Fiche mémo"])
    assert "abstention" in html.lower()


def test_abstention_sanction_claim_is_nuanced_not_absolute():
    """La sanction de l'abstention existe légalement mais n'est plus appliquée depuis
    2003 (vérifié auprès d'une source citoyenne qui rapporte le texte légal, FSE10 § 11) :
    le cours ne doit jamais présenter la sanction comme systématique."""
    html = render_markdown(_sections_by_title()["FSE10 — Théorie : notions et définitions"])
    text = html.lower()
    assert "rarement appliquée" in text or "rarement" in text


def test_bank_question_distinguishes_blank_vote_from_abstention():
    import importlib

    fse_bank = importlib.import_module("app.v1.fse_bank")
    import inspect

    source = inspect.getsource(fse_bank.import_fse10_to_bank)
    assert "ne pas se présenter au bureau de vote" in source
    assert "abstention" in source.lower()


def test_fse10_still_has_14_questions_7_4_3_distribution(db_session):
    from app.models import UAA, Module
    from app.seed import seed
    from app.v1.fse_bank import import_fse10_to_bank
    from app.v1.fse_plan import FSE_MODULE_CODE
    from app.v1.models import Question, QuestionDifficulty
    from collections import Counter

    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug="fse-fse10").first()
    import_fse10_to_bank(db_session, module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert len(questions) == 14
    counts = Counter(q.difficulty_declared for q in questions)
    assert counts == {
        QuestionDifficulty.EASY: 7,
        QuestionDifficulty.MEDIUM: 4,
        QuestionDifficulty.HARD: 3,
    }


def test_reseed_on_pre_ticket131_state_refreshes_comparer_and_memo_blocks(db_session):
    """Même bug de rafraîchissement que trouvé au ticket #126 pour FSE04 : si le titre
    d'un bloc ne change pas, _seed_uaa ne le remplace jamais sans obsolete_titles."""
    from app.models import UAA, BlockType, LessonBlock, Module
    from app.seed import seed
    from app.v1.fse_plan import FSE_MODULE_CODE

    seed()

    uaa = db_session.query(UAA).join(Module).filter(
        Module.code == FSE_MODULE_CODE, UAA.code == "FSE10"
    ).first()

    for title in ("FSE10 — Comparer pour ne pas confondre", "FSE10 — Fiche mémo"):
        block = db_session.query(LessonBlock).filter_by(uaa_id=uaa.id, title=title).first()
        block.content = "<p>Ancien contenu pré-ticket #131, qui ne distingue pas les deux notions visées.</p>"
        block.type = BlockType.MARKDOWN
    db_session.commit()

    seed()

    db_session.expire_all()
    for title in ("FSE10 — Comparer pour ne pas confondre", "FSE10 — Fiche mémo"):
        refreshed = db_session.query(LessonBlock).filter_by(uaa_id=uaa.id, title=title).first()
        assert "abstention" in refreshed.content.lower(), f"{title} pas rafraîchi"

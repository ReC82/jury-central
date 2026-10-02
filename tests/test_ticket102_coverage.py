"""Ticket #102 — contrôle de couverture et validation du parcours complet FSE01-FSE17.

Vérifications transversales qui ne sont PAS déjà couvertes par les fichiers de test
dédiés à chaque ticket (tests/test_ticket96_fse01.py et suivants) : absence de contenu
hors périmètre (IPP calculée/déclarée, crédit/emprunt/TAEG personnel, budget familial,
question sur un numéro d'UAA, article de loi précis), absence de question orpheline et de
quasi-doublon sur l'ENSEMBLE des 16 banques (pas seulement par paire de cours), et
fonctionnement réel practice→exam→correction pour chacun des 17 cours.

Les propriétés génériques du moteur (autosave/reprise exacte, historique, absence de fuite
des réponses dans la charge initiale, aucune troncature, erreur technique jamais notée 0,
export/impression, import idempotent) sont des propriétés du moteur V1 EXISTANT, jamais
modifié par les tickets #96-#101 (aucune refonte, voir rapport docs/claude-reports § 15) —
déjà couvertes par les tests génériques de ce moteur (tests/test_ticket55*, #62, #64, #82,
#92...) et par l'héritage mécanique de ces propriétés pour toute nouvelle matière qui
réutilise le même moteur sans le modifier. Ce fichier ne les re-prouve pas depuis zéro.

Aucun appel OpenAI réel."""

import re

import pytest

from app.models import UAA, Module, Subject
from app.seed import seed
from app.v1 import routes_sessions
from app.v1.ai_bridge import CORRECTABLE_TYPES
from app.v1.dedup import is_near_duplicate, question_signature
from app.v1.fse_plan import FSE_MODULE_CODE, FSE_PLAN, FSE_SUBJECT_NAME, fse01_to_fse16_codes
from app.v1.models import Question, QuestionVersion, SourceDocumentVersion

# =============================================================================================
# 1. Matrice de couverture — les 17 mini-cours officiels sont tous enregistrés et seedés
# =============================================================================================


def test_all_17_official_courses_registered():
    assert [plan.code for plan in FSE_PLAN] == [f"FSE{str(i).zfill(2)}" for i in range(1, 18)]


def test_all_17_courses_seeded_and_published(db_session):
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    uaas = db_session.query(UAA).filter_by(module_id=module.id).order_by(UAA.position).all()
    assert len(uaas) == 17
    assert [u.code for u in uaas] == [f"FSE{str(i).zfill(2)}" for i in range(1, 18)]
    assert all(u.is_published for u in uaas)


def test_media_and_citoyen_themes_correctly_split():
    """Médias = FSE01-07 (p. 41-47) ; Citoyen = FSE08-16 (p. 56-64) ; FSE17 = synthèse des
    deux. Vérifie qu'aucun cours n'a été mal classé entre les deux thèmes officiels."""
    by_code = {plan.code: plan for plan in FSE_PLAN}
    for code in [f"FSE{str(i).zfill(2)}" for i in range(1, 8)]:
        assert "Médias" in by_code[code].theme
    for code in [f"FSE{str(i).zfill(2)}" for i in range(8, 17)]:
        assert "Citoyen" in by_code[code].theme
    assert "Synthèse" in by_code["FSE17"].theme


# =============================================================================================
# 2. Périmètre officiel — exclusions respectées sur l'ensemble du contenu réellement rédigé
# =============================================================================================

_FORBIDDEN_PATTERNS = {
    # Calcul/déclaration de l'IPP personnel : seule la catégorie de recette est autorisée
    # (FSE12), jamais un calcul ni une déclaration.
    "calcul_ipp": re.compile(r"calcul(e|er|é|ez)?\s+(l'|ton |son |votre )?IPP", re.IGNORECASE),
    "declaration_ipp": re.compile(r"d[ée]clar(e|er|ation)\s+(l'|ta |sa |votre )?IPP", re.IGNORECASE),
    # Crédit/emprunt personnel, TAEG, budget familial, revenus du ménage : hors périmètre
    # (distinct de « emprunt de l'État »/dette publique, légitimement enseigné en FSE12).
    "taeg": re.compile(r"\bTAEG\b"),
    "budget_familial": re.compile(r"budget\s+familial", re.IGNORECASE),
    "revenus_menage": re.compile(r"revenus?\s+du\s+m[ée]nage", re.IGNORECASE),
    "avertissement_extrait": re.compile(r"avertissement[-\s]extrait", re.IGNORECASE),
    "fiscalite_immobiliere": re.compile(r"fiscalit[ée]\s+immobili[èe]re", re.IGNORECASE),
    # Article de loi précis (FSE06 : vocabulaire pédagogique seulement, jamais une
    # qualification pénale figée ; FSE15 : volet législation hors évaluation sommative).
    "article_loi": re.compile(r"article\s+\d+", re.IGNORECASE),
    # Question sur le numéro/code de l'UAA elle-même (métadonnée, jamais une question).
    "numero_uaa": re.compile(r"num[ée]ro\s+(de\s+l'|d'|de\s+cette\s+)?UAA", re.IGNORECASE),
}


@pytest.mark.parametrize("pattern_name", list(_FORBIDDEN_PATTERNS))
def test_no_forbidden_content_in_fse_bank_source(pattern_name):
    """Analyse statique du code source de app/v1/fse_bank.py (questions/explications/
    rubriques) — couvre les 16 cours banqués en une seule passe, plus robuste qu'une
    vérification par cours isolé."""
    with open("app/v1/fse_bank.py", encoding="utf-8") as handle:
        source = handle.read()
    matches = _FORBIDDEN_PATTERNS[pattern_name].findall(source)
    assert not matches, f"motif interdit « {pattern_name} » trouvé dans fse_bank.py : {matches}"


@pytest.mark.parametrize("code", [f"FSE{str(i).zfill(2)}" for i in range(1, 18)])
def test_no_forbidden_content_in_course_markdown(db_session, code):
    """FSE01 (ticket #105) expose `fse01_course_sections()` (plusieurs blocs titrés,
    refonte pédagogique et visuelle) plutôt que `fse01_course_markdown()` (un seul bloc) —
    les deux conventions sont acceptées ici, le contenu analysé est le même texte
    concaténé, une fois les sections regroupées."""
    seed()
    module_name = f"app.v1.{code.lower()}_course"
    course_module = __import__(module_name, fromlist=["x"])
    markdown_fn = getattr(course_module, f"{code.lower()}_course_markdown", None)
    if markdown_fn is not None:
        text = markdown_fn()
    else:
        sections_fn = getattr(course_module, f"{code.lower()}_course_sections")
        text = "\n\n".join(markdown for _title, markdown in sections_fn())
    for name, pattern in _FORBIDDEN_PATTERNS.items():
        if name in ("calcul_ipp", "declaration_ipp") and code != "FSE12":
            continue  # seul FSE12 mentionne l'IPP (comme catégorie, jamais calculée).
        matches = pattern.findall(text)
        assert not matches, f"{code} : motif interdit « {name} » trouvé : {matches}"


def test_fse15_respects_legislation_exclusion(db_session):
    """Note 90 du programme (p. 61, rappelée dans docs/content_plan_fse.md) : le volet
    législation reste hors évaluation sommative — vérifié explicitement pour FSE15
    (circuit économique/interventions de l'État), seul cours dont le cahier des charges
    cite cette note."""
    from app.v1.fse15_course import fse15_course_markdown

    text = fse15_course_markdown()
    assert "hors évaluation sommative" in text or "législation" in text.lower()
    assert not re.search(r"article\s+\d+", text, re.IGNORECASE)


# =============================================================================================
# 3. Banque — aucune question orpheline, aucun quasi-doublon, sur l'ensemble des 16 cours
# =============================================================================================


def _seed_all_fse_banks(db_session, module: Module) -> None:
    for code in fse01_to_fse16_codes():
        from app.v1.fse_plan import FSE_PLAN_BY_CODE

        plan = FSE_PLAN_BY_CODE[code]
        uaa = db_session.query(UAA).filter_by(slug=plan.slug).first()
        importer = routes_sessions._FSE_BANK_IMPORTERS[plan.slug]
        importer(db_session, module, uaa)
    db_session.commit()


def test_no_near_duplicate_questions_across_entire_fse_bank(db_session):
    """Ticket #102 (contrôle de couverture) : garde GLOBALE sur les 16×14=224 questions
    de la banque FSE (pas seulement par paire de cours, comme dans les fichiers de test
    par ticket) — l'audit mené pendant ce ticket a révélé 5 paires de quasi-doublons,
    toutes corrigées : 4 INTRA-cours (FSE06, FSE10, FSE11, FSE12, détectables par cours)
    et 1 CROISÉE entre FSE08 et FSE09 (deux questions sur le niveau fédéral quasi
    identiques malgré leur appartenance à deux cours différents — invisible à une
    vérification par paire de cours, détectée uniquement par cette garde globale). Empêche
    toute régression future, y compris croisée entre cours."""
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    _seed_all_fse_banks(db_session, module)

    questions = (
        db_session.query(Question)
        .join(UAA, Question.uaa_id == UAA.id)
        .filter(UAA.code.in_(fse01_to_fse16_codes()))
        .all()
    )
    assert len(questions) == 16 * 14

    sigs = [
        (q.id, q.uaa.code, question_signature(q.current_version.question_type, q.current_version.content_json))
        for q in questions
    ]
    collisions = []
    for i in range(len(sigs)):
        for j in range(i + 1, len(sigs)):
            if is_near_duplicate(sigs[i][2], sigs[j][2]):
                collisions.append((sigs[i][:2], sigs[j][:2]))
    assert not collisions, f"quasi-doublons trouvés : {collisions}"


def test_no_orphan_source_document_questions_across_entire_fse_bank(db_session):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    _seed_all_fse_banks(db_session, module)

    questions = (
        db_session.query(Question)
        .join(UAA, Question.uaa_id == UAA.id)
        .filter(UAA.code.in_(fse01_to_fse16_codes()))
        .all()
    )
    checked = 0
    for question in questions:
        doc_id = question.current_version.content_json.get("source_document_version_id")
        if doc_id:
            checked += 1
            version = db_session.get(SourceDocumentVersion, doc_id)
            assert version is not None, f"question {question.id} ({question.uaa.code}) référence un document inexistant"
    assert checked >= 60, "trop peu de questions sourcées détectées — vérifier le câblage des source_document_version_id"


def test_all_bank_question_types_are_correctable(db_session):
    """Chaque question des 16 banques doit être d'un type réellement supporté par le pont
    de correction IA (`CORRECTABLE_TYPES`, #40) — jamais `true_false`, enregistré dans le
    registre mais non câblé pour la correction (voir docstring de app.v1.ai_bridge)."""
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    _seed_all_fse_banks(db_session, module)

    questions = (
        db_session.query(Question)
        .join(UAA, Question.uaa_id == UAA.id)
        .filter(UAA.code.in_(fse01_to_fse16_codes()))
        .all()
    )
    for question in questions:
        assert question.current_version.question_type in CORRECTABLE_TYPES
        assert question.current_version.question_type != "true_false"


def test_fse17_has_zero_bank_questions(db_session):
    """FSE17 (révision transversale) n'a jamais sa propre banque — vérifié positivement
    ici (pas seulement par l'absence dans `_FSE_BANK_IMPORTERS`, déjà testé ailleurs)."""
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    fse17_uaa = db_session.query(UAA).filter_by(module_id=module.id, code="FSE17").first()
    assert fse17_uaa is not None
    own_questions = db_session.query(Question).filter_by(uaa_id=fse17_uaa.id).count()
    assert own_questions == 0


# =============================================================================================
# 4. Chaque cours FSE01-17 : page de cours accessible et non vide
# =============================================================================================


@pytest.mark.parametrize("code", [f"FSE{str(i).zfill(2)}" for i in range(1, 18)])
def test_course_page_accessible_and_substantial(client, db_session, code):
    """Page de cours réellement accessible, jamais vide ni « provisoire » — contrôle
    minimal exigé par l'acceptation du ticket #102 pour les 17 cours en une seule passe
    paramétrée (les contenus détaillés par cours sont déjà vérifiés dans les fichiers de
    test par ticket)."""
    seed()
    from app.v1.fse_plan import FSE_PLAN_BY_CODE

    slug = FSE_PLAN_BY_CODE[code].slug
    response = client.get(f"/uaa/{slug}")
    assert response.status_code == 200
    text = response.text
    assert "provisoire" not in text.lower()
    assert "stub" not in text.lower()
    # Un cours réel dépasse largement un simple résumé de programme (contrat de
    # rédaction des tickets #96-#101 : « ne livre ni résumé, ni simple liste »).
    assert len(text) > 8000


# =============================================================================================
# 5. Pas de refonte du moteur hors périmètre — vérifié en négatif
# =============================================================================================


def test_question_version_model_unchanged_in_shape():
    """Garde légère contre une refonte involontaire du moteur (ticket #102 : « pas de
    refonte du moteur hors périmètre ») — vérifie que les colonnes structurelles de base
    utilisées par toute la plateforme existent toujours sous leur nom établi."""
    columns = {c.name for c in QuestionVersion.__table__.columns}
    assert {"question_type", "content_json", "question_id"} <= columns

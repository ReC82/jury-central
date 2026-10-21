"""Ticket #136 (complément du 21/10) — séquence finale « À retenir » : synthèse, « Ce que je
dois savoir faire », vocabulaire en fiches. Construite à partir du contenu déjà publié,
sans doublon des sections mémo existantes ni perte de contenu."""

import re

from app.models import UAA, BlockSpace, BlockType, LessonBlock, Module, Subject
from app.v1.course_memo import BlockSource, build_course_memo

AMPCR_MC05 = """# Alimentation, refroidissement, ESD et sécurité électrique

## 1. Ce qu'il faut savoir
L'alimentation convertit le courant secteur.

## 2. Définitions essentielles
- **PSU** (Power Supply Unit) : bloc d'alimentation, caractérisé par sa puissance
  nominale (en watts).
- **ESD** (ElectroStatic Discharge) : décharge d'électricité statique.

## 4. Procédure / méthode
Avant toute intervention : (1) éteindre et débrancher le PC du secteur ; (2) se décharger
de l'électricité statique ; (3) manipuler les composants par les bords.

## 6. Pièges fréquents
- Sous-dimensionner l'alimentation.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Bloc d'alimentation | Power supply unit (PSU) |
| Dissipateur thermique | Heatsink |

## 8. À retenir pour l'examen
- ATX 24 broches = carte mère ; EPS = CPU.
- Toujours débrancher le secteur avant d'ouvrir un PC.
"""

FSE_THEORY = """<div class="jc-prose"><p>Texte.</p></div>
<div class="jc-definitions">
<div class="jc-definition">
<span class="jc-definition-term">Interactivité</span>
<p class="jc-definition-body">possibilité, pour le récepteur, de réagir au message.</p>
</div>
<div class="jc-definition">
<span class="jc-definition-term">Audience</span>
<p class="jc-definition-body">le nombre de personnes qui consultent un média.</p>
</div>
</div>"""

FSE_COMPARE = """> **Supposer qu'un média combine un seul mode de financement** : faux.

> **Confondre interactivité et mode de financement** : deux notions indépendantes."""

FSE_MEMO = "- Quatre modes de financement, souvent combinés.\n- Un compteur de vues mesure l'audience."


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _course(db, module_code, uaa_code, slug, blocks):
    subject = Subject(name=f"S {module_code}", slug=f"s-{module_code.lower()}")
    db.add(subject)
    db.flush()
    module = Module(code=module_code, slug=module_code.lower(), subject_id=subject.id)
    db.add(module)
    db.flush()
    uaa = UAA(code=uaa_code, title=f"Cours {uaa_code}", slug=slug, position=1,
              is_published=True, module_id=module.id)
    db.add(uaa)
    db.flush()
    for position, (title, content) in enumerate(blocks, start=1):
        db.add(LessonBlock(uaa_id=uaa.id, title=title, type=BlockType.MARKDOWN, content=content,
                           position=position, space=BlockSpace.COURSE, is_published=True))
    db.commit()
    return uaa


# --- Construction ----------------------------------------------------------------------


def test_ampcr_memo_absorbs_memo_sections_and_builds_vocabulary():
    memo = build_course_memo("AMPCR", "MC05", "ampcr-mc05", "MC05",
                             [BlockSource(1, "Cours de révision express", AMPCR_MC05)])
    assert memo is not None
    assert memo.absorbed_sections == {1: {"7. Vocabulaire FR / EN", "8. À retenir pour l'examen"}}
    assert "Toujours débrancher le secteur" in memo.summary_html
    psu = next(c for c in memo.vocabulary if c.term == "PSU")
    assert psu.expansion == "Power Supply Unit"
    assert "puissance nominale" in psu.definition_html
    assert "PSU" in psu.english  # ligne FR/EN rattachée par l'acronyme
    assert psu.landmark  # repère du lexique AMPCR (#84) pour MC05
    assert [c.term for c in memo.pairs] == ["Dissipateur thermique"]
    assert memo.method_title == "Avant toute intervention"
    assert len(memo.method_steps) == 3
    assert memo.objective  # objectif du plan AMPCR validé


def test_fse_memo_uses_plan_skills_definitions_and_explicit_confusions_only():
    blocks = [
        BlockSource(1, "FSE02 — Théorie : notions et définitions", FSE_THEORY),
        BlockSource(2, "FSE02 — Comparer pour ne pas confondre", FSE_COMPARE),
        BlockSource(3, "FSE02 — Fiche mémo", FSE_MEMO),
    ]
    memo = build_course_memo("FSE", "FSE02", "fse-fse02", "FSE02", blocks)
    assert memo.absorbed_block_ids == {3}
    assert memo.skills and "mode" in memo.skills[0]
    cards = {c.term: c for c in memo.vocabulary}
    assert cards["Interactivité"].definition_html.startswith("Possibilité")
    assert "Confondre interactivité" in cards["Interactivité"].confusion_html
    assert not cards["Audience"].confusion_html  # « Supposer… » n'est pas une confusion de terme


def test_no_memo_for_transversal_revisions_and_out_of_scope_subjects():
    body = [BlockSource(1, "x", "## À retenir\n- a\n")]
    assert build_course_memo("AMPCR", "MC38", "ampcr-mc38", "MC38", body) is None
    assert build_course_memo("MB32", "UAA1", "mb32-uaa1", "UAA1", body) is None
    assert build_course_memo("AMPCR", "MC06", "ampcr-mc06", "MC06",
                             [BlockSource(1, "x", "## 1. Ce qu'il faut savoir\ntexte")]) is None


# --- Page de cours ---------------------------------------------------------------------


def test_single_body_course_gets_one_final_memo_sequence_without_duplicate(client, db_session):
    _course(db_session, "AMPCR", "MC05", "ampcr-mc05", [("Cours de révision express", AMPCR_MC05)])
    page = client.get("/uaa/ampcr-mc05").text
    text = _text(page)
    assert "8. À retenir pour l'examen" not in page
    assert "7. Vocabulaire FR / EN" not in page
    assert page.count('id="a-retenir"') == 1
    assert "6. Pièges fréquents" in page  # sections d'enseignement inchangées
    # Aucune perte : synthèse et lignes du tableau FR/EN présentes dans la fiche
    for fragment in ("Toujours débrancher le secteur avant d'ouvrir un PC.", "Heatsink",
                     "Dissipateur thermique", "Ce que je dois savoir faire",
                     "Le vocabulaire à retenir"):
        assert fragment in text
    # La fiche est le dernier h2 du conteneur → dernière séquence
    headings = re.findall(r"<h2[^>]*>(.*?)</h2>", page.split('id="jc-lesson"')[1])
    assert headings[-1] == "À retenir"


def test_multi_card_course_moves_memo_card_last(client, db_session):
    _course(db_session, "FSE", "FSE02", "fse-fse02", [
        ("FSE02 — Théorie : notions et définitions", FSE_THEORY),
        ("FSE02 — Comparer pour ne pas confondre", FSE_COMPARE),
        ("FSE02 — Fiche mémo", FSE_MEMO),
        ("FSE02 — Sources officielles vérifiées", "Programme officiel."),
    ])
    page = client.get("/uaa/fse-fse02").text
    lesson = page.split('id="jc-lesson"')[1]
    titles = re.findall(r'<h2 class="jc-card-title h5">(.*?)</h2>', lesson)
    assert titles[-1] == "À retenir"
    assert "FSE02 — Fiche mémo" not in titles
    assert "Un compteur de vues mesure l&#39;audience." in page or "Un compteur de vues mesure l'audience." in page
    assert "Identifier le ou les modes de financement" in page


def test_course_without_memo_source_is_unchanged(client, db_session):
    _course(db_session, "MB32", "UAA1", "mb32-uaa1", [("Fiche mémo", "- a\n- b")])
    page = client.get("/uaa/mb32-uaa1").text
    assert "jc-memo" not in page
    assert "Fiche mémo" in page

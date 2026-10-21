"""Ticket #65 — bug de rendu Markdown : `>` interprété comme encadré ATTENTION.

Bug reporté : dans le contenu Informatique (MC08 — Partitionnement, GPT/MBR et
formatage), une phrase repliée sur plusieurs lignes plaçait accidentellement
`> 2 To` en tout début de ligne. Markdown standard interprète toute ligne
commençant par `>` comme une citation (blockquote), et
`wrapBlockquotesAsWarningCards` (app/static/js/design_system.js) transforme
ensuite systématiquement chaque `<blockquote>` en encadré rouge « ⚠️ Attention »
— coupant la phrase et faisant croire à un avertissement inexistant.

Le correctif est un correctif de contenu (repli de ligne différent dans
app/v1/ampcr_courses.py, MC08), pas un changement du moteur de rendu : les
vrais encadrés ATTENTION (ex. les blocs « Piège fréquent » du contenu Français
dans app/seed.py) doivent continuer à fonctionner à l'identique.
"""

import re

from app.content import render_markdown
from app.models import UAA, LessonBlock, Module, Subject
from app.seed import (
    MC08_GREATER_THAN_FIXED_FRAGMENT,
    MC08_GREATER_THAN_STALE_FRAGMENT,
    repair_mc08_greater_than_line,
)
from app.v1.ampcr_courses import AMPCR_COURSE_MARKDOWN


def test_mc08_gpt_mbr_greater_than_comparison_stays_inline():
    """Cas exact du ticket : `disque > 2 To` doit rester dans la phrase."""
    html = render_markdown(AMPCR_COURSE_MARKDOWN["MC08"])

    assert "<blockquote>" not in html
    # Le ">" reste un simple caractère de comparaison dans un paragraphe normal,
    # donc échappé en entité HTML par le moteur Markdown (pas un marqueur de citation).
    assert "disque &gt; 2 To" in html


def test_mc08_procedure_paragraph_is_a_single_unbroken_paragraph():
    """La phrase de la procédure ne doit pas être coupée en deux paragraphes."""
    html = render_markdown(AMPCR_COURSE_MARKDOWN["MC08"])
    match = re.search(
        r"<p>Avant de partitionner/formater un disque.*?ext4 pour Linux\)\.</p>",
        html,
        re.DOTALL,
    )
    assert match is not None, html


def _greater_than_line_blocks(text: str) -> list[list[str]]:
    """Reproduit la logique d'audit : regroupe les lignes consécutives commençant
    par '>' en blocs (blockquotes Markdown), pour repérer les déclenchements
    accidentels de la syntaxe de citation."""
    lines = text.splitlines()
    blocks: list[list[str]] = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith(">"):
            start = i
            while i < len(lines) and lines[i].strip().startswith(">"):
                i += 1
            blocks.append(lines[start:i])
        else:
            i += 1
    return blocks


def test_no_accidental_blockquote_triggers_in_informatique_course_content():
    """Garde de non-régression (§ audit du ticket #65) : à ce jour, aucun cours
    Informatique (AMPCR_COURSE_MARKDOWN) n'utilise de citation Markdown
    intentionnelle — toute ligne commençant par '>' y est donc un bug de repli
    de ligne accidentel, jamais un encadré voulu."""
    offenders = []
    for code, text in AMPCR_COURSE_MARKDOWN.items():
        for block in _greater_than_line_blocks(text):
            offenders.append((code, block))

    assert offenders == []


def test_no_line_start_angle_bracket_outside_known_html_blocks_in_informatique_content():
    """Audit du second symbole demandé par le ticket (`<`). Les seules lignes
    commençant par '<' dans le contenu Informatique doivent être du HTML brut
    intentionnel (balises), jamais une comparaison numérique du type
    "< 3 Go" repliée en début de ligne."""
    tag_start = re.compile(r"^<[a-zA-Z/]")
    offenders = []
    for code, text in AMPCR_COURSE_MARKDOWN.items():
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("<") and not tag_start.match(stripped):
                offenders.append((code, line))

    assert offenders == []


def test_intentional_attention_blockquotes_in_french_content_are_unaffected():
    """Ne pas casser les vrais encadrés ATTENTION : les blocs « Piège fréquent »
    du contenu Français (app/seed.py) doivent continuer à être rendus comme de
    vraies citations Markdown, puisqu'ils sont volontaires et écrits comme des
    blocs '>' complets sur toutes leurs lignes."""
    from app.seed import _SOLIDES_COURSE

    html = render_markdown(_SOLIDES_COURSE)
    assert "<blockquote>" in html
    assert "Piège fréquent" in html


def test_no_accidental_blockquote_triggers_in_seed_content():
    """Même garde d'audit que ci-dessus, appliquée au contenu déjà présent dans
    app/seed.py (non modifié ici, Français en pause) : tout bloc '>' détecté doit
    être un encadré Piège/ATTENTION volontaire, jamais un repli accidentel."""
    from app import seed as seed_module

    source = seed_module.__file__
    with open(source, encoding="utf-8") as fh:
        raw = fh.read()

    offenders = []
    for block in _greater_than_line_blocks(raw):
        joined = "\n".join(block)
        if "Piège" not in joined and "ATTENTION" not in joined.upper():
            offenders.append(block)

    assert offenders == []


# --- Base déjà seedée avec l'ancien repli de ligne (contenu réellement servi) ---

def _make_block(db_session, code: str, content: str) -> LessonBlock:
    subject = Subject(name=f"Info test {code}", slug=f"info-test-{code.lower()}")
    db_session.add(subject)
    db_session.flush()
    module = Module(subject_id=subject.id, code="AMPCR", slug=f"ampcr-test-{code.lower()}")
    db_session.add(module)
    db_session.flush()
    uaa = UAA(code=code, title="t", slug=f"{code.lower()}-test", position=1,
              is_published=True, module_id=module.id)
    db_session.add(uaa)
    db_session.flush()
    block = LessonBlock(uaa=uaa, title="Cours de révision express", type="markdown",
                        content=content, position=1)
    db_session.add(block)
    db_session.commit()
    return block


def test_stale_fragment_reproduces_the_bug():
    html = render_markdown("Avant de partitionner : " + MC08_GREATER_THAN_STALE_FRAGMENT)
    assert "<blockquote>" in html


def test_fixed_fragment_is_the_one_in_current_course():
    assert MC08_GREATER_THAN_FIXED_FRAGMENT in AMPCR_COURSE_MARKDOWN["MC08"]
    assert MC08_GREATER_THAN_STALE_FRAGMENT not in AMPCR_COURSE_MARKDOWN["MC08"]


def test_repair_replaces_only_the_stale_fragment_and_is_idempotent(db_session):
    content = (
        "# MC08 (édité depuis l'admin)\n\n## 4. Procédure\nAvant de partitionner : "
        + MC08_GREATER_THAN_STALE_FRAGMENT
        + "\n\n> **Piège fréquent** : vrai encadré conservé.\n"
    )
    block = _make_block(db_session, "MC08", content)

    assert repair_mc08_greater_than_line(db_session) == 1
    db_session.commit()
    db_session.refresh(block)

    assert block.content.startswith("# MC08 (édité depuis l'admin)")
    assert MC08_GREATER_THAN_FIXED_FRAGMENT in block.content
    html = render_markdown(block.content)
    assert "disque &gt; 2 To" in html
    # Seul le vrai encadré reste une citation.
    assert html.count("<blockquote>") == 1
    assert "Piège fréquent" in html.split("<blockquote>")[1]

    assert repair_mc08_greater_than_line(db_session) == 0


def test_repair_ignores_other_uaas_and_modified_text(db_session):
    other = _make_block(db_session, "MC09", MC08_GREATER_THAN_STALE_FRAGMENT)
    edited = _make_block(db_session, "MC08", "Texte réécrit depuis l'admin\n> 2 To ici.")

    assert repair_mc08_greater_than_line(db_session) == 0
    db_session.refresh(other)
    db_session.refresh(edited)
    assert other.content == MC08_GREATER_THAN_STALE_FRAGMENT
    assert edited.content == "Texte réécrit depuis l'admin\n> 2 To ici."

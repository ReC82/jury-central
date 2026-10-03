"""Transformation générique Markdown → blocs de cours titrés pour les mini-cours FSE02 à
FSE16 (refonte pédagogique et visuelle, ticket #105, étape 5 — extension au-delà de FSE01).

FSE02-FSE16 partagent tous la même structure en 10 sections numérotées, parfois suivie
d'une 11e section « Sources officielles vérifiées » (tickets #96-#101) :
1. Ce que tu dois savoir faire à l'examen — 2. Théorie progressive — 3. Définitions
importantes — 4. Méthode étape par étape — 5. Exemples commentés — 6. Mauvaises réponses
comparées aux bonnes — 7. Pièges et erreurs fréquentes — 8. Exercices guidés —
9. Corrigés très expliqués — 10. Fiche mémo — [11. Sources officielles vérifiées].

Ce module découpe cette structure en plusieurs blocs titrés (même logique que FSE01, voir
`app.v1.fse01_course`), SANS réécrire la prose déjà rédigée et validée pour chaque cours :
seules des transformations mécaniques, sûres et vérifiées sont appliquées.

Composants visuels ajoutés — seulement là où le contenu s'y prête déjà réellement, jamais
un même gabarit forcé partout (demande explicite du ticket #105 § 5) :
- « Mauvaises réponses comparées aux bonnes » devient une grille de comparaison
  (`.jc-compare`, variante bad/good) : ce contenu EST déjà une comparaison directe, au
  format strictement répété « - ❌ **Mauvaise réponse** ... / - ✅ **Bonne réponse** ... »
  dans les 15 cours (vérifié avant d'écrire ce module).
- « Pièges et erreurs fréquentes » devient des citations Markdown (`> ...`), converties
  automatiquement en WarningCard par `design_system.js`
  (`wrapBlockquotesAsWarningCards()`, déjà existant) : ce contenu EST déjà un piège.
- « Définitions importantes » et « Exemples commentés » restent des listes/paragraphes
  (ligne vide corrigée), affichés dans leur carte appropriée — pas de grille de
  définitions forcée : certaines puces de définitions regroupent plusieurs termes (ex.
  loi/décret/ordonnance dans FSE08), ce qui ne se prête pas à un découpage automatique
  fiable terme par terme sans risquer de couper un terme au mauvais endroit.
- Un schéma SVG n'est ajouté qu'aux cours dont la notion centrale est un schéma
  relationnel réel (FSE08 : niveaux de pouvoir ; FSE15 : circuit économique) — ajouté
  directement dans `app.v1.fse08_course`/`app.v1.fse15_course`, pas ici.

Bug corrigé par ce module (diagnostic ticket #105 § 1) : une liste Markdown non précédée
d'une ligne vide est fondue par `app.content.render_markdown` (bibliothèque `markdown`,
extensions `fenced_code`/`tables`, sans `sane_lists`) dans le paragraphe précédent, sous
forme de texte brut à tirets littéraux — `fix_list_blank_lines()` l'évite systématiquement."""

import re

_SECTION_RE = re.compile(r"^## (\d+)\. (.+?)\s*$", re.MULTILINE)
_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")


def parse_numbered_sections(markdown: str) -> dict[int, str]:
    """{numéro de section : contenu brut, sans le titre '## N. ...' ni le H1}."""
    matches = list(_SECTION_RE.finditer(markdown))
    sections: dict[int, str] = {}
    for i, m in enumerate(matches):
        num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        sections[num] = markdown[start:end].strip("\n")
    return sections


def fix_list_blank_lines(text: str) -> str:
    """Insère une ligne vide avant toute liste Markdown qui n'en a pas déjà une."""
    lines = text.split("\n")
    out: list[str] = []
    prev_blank_or_list = True
    for line in lines:
        is_list = bool(_LIST_ITEM_RE.match(line))
        if is_list and not prev_blank_or_list and out and out[-1].strip():
            out.append("")
        out.append(line)
        prev_blank_or_list = is_list or not line.strip()
    return "\n".join(out)


_BAD_LABEL_RE = re.compile(r"^\*\*Mauvaise réponse\*\*\s*:?\s*")
_GOOD_LABEL_RE = re.compile(r"^\*\*Bonne réponse\*\*\s*:?\s*")


def mauvaises_bonnes_to_comparegrid(text: str) -> str:
    """Convertit chaque paire de puces « - ❌ **Mauvaise réponse** ... » / « - ✅ **Bonne
    réponse** ... » en une grille de comparaison visuelle (`.jc-compare`). Toute puce qui
    ne fait pas partie d'une paire reconnue est laissée inchangée (comportement sûr par
    défaut)."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    blocks: list[str] = []
    i = 0
    while i < len(lines):
        current = lines[i]
        if (
            current.startswith("- ❌")
            and i + 1 < len(lines)
            and lines[i + 1].startswith("- ✅")
        ):
            bad_body = _BAD_LABEL_RE.sub("", current[len("- ❌"):].strip())
            good_body = _GOOD_LABEL_RE.sub("", lines[i + 1][len("- ✅"):].strip())
            blocks.append(
                '<div class="jc-compare">\n'
                '<div class="jc-compare-item jc-compare-item--bad">\n'
                '<span class="jc-compare-label">❌ Mauvaise réponse</span>\n'
                f"<p>{bad_body}</p>\n"
                "</div>\n"
                '<div class="jc-compare-item jc-compare-item--good">\n'
                '<span class="jc-compare-label">✅ Bonne réponse</span>\n'
                f"<p>{good_body}</p>\n"
                "</div>\n"
                "</div>"
            )
            i += 2
        else:
            blocks.append(current)
            i += 1
    return "\n\n".join(blocks)


_EXEMPLE_HEADER_RE = re.compile(r"^### (Exemple .+)$", re.MULTILINE)


def exemple_headers_to_titles(text: str) -> str:
    """Convertit chaque titre Markdown `### Exemple N — ...` en
    `<h3 class="jc-example-title">` (HTML brut, pour porter la classe d'espacement dédiée
    — 32px avant/16px après, voir `docs/components/ExampleTitle.md`, tickets #112/#115)."""
    return _EXEMPLE_HEADER_RE.sub(r'<h3 class="jc-example-title">\1</h3>', text)


_ANALYSE_RE = re.compile(r"\*\*Analyse comment[ée]e\s*:\*\*\s*")
_DECRYPT_TITLE_HTML = (
    '<h4 class="jc-decrypt-title"><span aria-hidden="true">🔍</span> '
    "Décryptons ce document</h4>"
)


def analyse_commentee_to_decrypt(text: str) -> str:
    """Remplace `**Analyse commentée :**` par le titre dédié « Décryptons ce document »
    (voir `docs/components/DecryptTitle.md`, tickets #112/#115), en séparant le texte qui
    suit dans son propre paragraphe."""
    return _ANALYSE_RE.sub(f"\n\n{_DECRYPT_TITLE_HTML}\n\n", text)


_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _inline_md_to_html(text: str) -> str:
    """Convertit le gras Markdown (`**...**`) en `<strong>` — nécessaire car ce texte est
    inséré dans un bloc HTML brut, jamais retraité par `render_markdown` (voir docstring
    du module, tickets #112/#115)."""
    return _BOLD_RE.sub(r"<strong>\1</strong>", text)


_LIST_LINE_RE = re.compile(r"^(-|\d+\.)\s+")


def _paragraphs_to_html(text: str) -> str:
    """Convertit un texte brut (paragraphes séparés par une ligne vide, gras `**...**`) en
    HTML réel : un paragraphe dont CHAQUE ligne est un élément de liste (`- ...`/`N. ...`)
    devient un vrai `<ul>`/`<ol>`, les autres deviennent des `<p>`. Nécessaire car ce texte
    est inséré dans un bloc HTML brut (`<details>`), jamais retraité par
    `render_markdown` — c'est la cause exacte des listes à tirets/numéros restées
    littérales dans certains corrigés (ex. FSE03), diagnostiquée au ticket #112/#115."""
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    html_blocks: list[str] = []
    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if lines and all(_LIST_LINE_RE.match(line) for line in lines):
            ordered = bool(re.match(r"^\d+\.\s", lines[0]))
            tag = "ol" if ordered else "ul"
            items = "\n".join(
                f"<li>{_inline_md_to_html(_LIST_LINE_RE.sub('', line))}</li>" for line in lines
            )
            html_blocks.append(f"<{tag}>\n{items}\n</{tag}>")
        else:
            paragraph = " ".join(lines)
            html_blocks.append(f"<p>{_inline_md_to_html(paragraph)}</p>")
    return "\n".join(html_blocks)


def _is_raw_html_block(block: str) -> bool:
    """Un bloc déjà en HTML brut (ex. schéma SVG inséré par substitution f-string dans la
    théorie de FSE08/FSE15, voir `FSE08_POWER_LEVELS_DIAGRAM_SVG`/
    `FSE15_CIRCUIT_DIAGRAM_SVG`) — à laisser tel quel, jamais enveloppé dans un `<p>`."""
    return block.lstrip().startswith("<")


def theory_prose_to_html(text: str) -> str:
    """Convertit la prose théorique (ticket #120) en HTML littéral, groupée en un ou
    plusieurs `<div class="jc-prose">` qui limitent la largeur de lecture à ~70 caractères
    par ligne — SAUF un bloc déjà en HTML brut (schéma SVG déjà existant dans certains
    cours), laissé tel quel et hors de cette contrainte de largeur, puisqu'il peut avoir
    besoin de toute la largeur disponible (« sans rétrécir... les documents qui ont besoin
    de largeur », cahier des charges du ticket #120).

    `fix_list_blank_lines()` est appliqué d'abord : une liste introduite par une phrase sur
    la même ligne de bloc (ex. « ... sont possibles :\\n- la vente : ... ») doit être
    séparée en son propre bloc avant d'être reconnue comme liste par `_paragraphs_to_html`
    — sans cette étape, elle resterait fondue en texte brut à tirets littéraux dans le
    paragraphe précédent (même bug que diagnostiqué au ticket #112)."""
    blocks = [b.strip() for b in fix_list_blank_lines(text).split("\n\n") if b.strip()]
    out: list[str] = []
    prose_buffer: list[str] = []

    def flush() -> None:
        if prose_buffer:
            out.append('<div class="jc-prose">\n' + "\n\n".join(prose_buffer) + "\n</div>")
            prose_buffer.clear()

    for block in blocks:
        if _is_raw_html_block(block):
            flush()
            out.append(block)
            continue
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if lines and all(_LIST_LINE_RE.match(line) for line in lines):
            ordered = bool(re.match(r"^\d+\.\s", lines[0]))
            tag = "ol" if ordered else "ul"
            items = "\n".join(
                f"<li>{_inline_md_to_html(_LIST_LINE_RE.sub('', line))}</li>" for line in lines
            )
            prose_buffer.append(f"<{tag}>\n{items}\n</{tag}>")
        else:
            paragraph = " ".join(lines)
            prose_buffer.append(f"<p>{_inline_md_to_html(paragraph)}</p>")
    flush()
    return "\n\n".join(out)


_DEFINITION_BULLET_RE = re.compile(
    r"^-\s+\*\*(?P<term>.+?)\*\*\s*(?P<qualifier>\([^)]*\))?\s*:\s*(?P<body>.+)$"
)


def _definitions_bullets_to_items(text: str) -> list[tuple[str, str]]:
    """Découpe chaque puce « - **Terme** (qualificatif optionnel) : explication. » en
    (terme affiché, corps HTML) — SANS JAMAIS découper à l'intérieur d'un terme groupé (ex.
    « Région (flamande, wallonne, Bruxelles-Capitale) » reste un seul terme avec son
    qualificatif, jamais trois cartes distinctes mal attribuées — risque identifié dans la
    docstring du module avant l'écriture de cette fonction). Toute puce qui ne correspond
    pas exactement à ce format (terme en gras suivi de « : ») est ignorée en toute sécurité
    plutôt que mal découpée : vérifié à l'écriture de ce module qu'elle couvre 100 % des
    puces de FSE02/FSE04-FSE16 (aucune puce ignorée en pratique)."""
    items: list[tuple[str, str]] = []
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("-"):
            continue
        m = _DEFINITION_BULLET_RE.match(line)
        if not m:
            continue
        term = m.group("term").strip()
        if m.group("qualifier"):
            term = f"{term} {m.group('qualifier').strip()}"
        items.append((term, _inline_md_to_html(m.group("body").strip())))
    return items


def theory_and_definitions_to_cards(theory_raw: str, definitions_raw: str) -> str:
    """Restructure la théorie progressive + la liste de définitions d'un cours FSE02-FSE16
    (ticket #120), sans perdre de matière : la prose devient du HTML littéral à largeur de
    lecture limitée (`theory_prose_to_html`), chaque définition devient une carte
    `.jc-definition` (terme jamais découpé, voir `_definitions_bullets_to_items`).

    Si TOUS les termes définis apparaissent déjà (en gras) dans la prose ci-dessus, la
    grille de définitions devient un lexique repliable (`.jc-glossary`, disponible à
    l'impression même fermé) — cohérent avec FSE03 (même ticket) : une définition qui n'est
    PAS déjà dite ailleurs dans les explications visibles n'est, elle, jamais cachée (reste
    une grille visible), pour ne jamais retirer une information nécessaire à l'examen."""
    theory_html = theory_prose_to_html(theory_raw)

    items = _definitions_bullets_to_items(definitions_raw)
    if not items:
        return theory_html

    prose_lower = theory_raw.lower()
    all_redundant = all(term.split("(")[0].strip().lower() in prose_lower for term, _ in items)

    grid = (
        '<div class="jc-definitions">\n'
        + "\n".join(
            f'<div class="jc-definition">\n<span class="jc-definition-term">{term}</span>\n'
            f'<p class="jc-definition-body">{body}</p>\n</div>'
            for term, body in items
        )
        + "\n</div>"
    )

    if all_redundant:
        definitions_html = (
            '<details class="jc-glossary">\n'
            "<summary>📖 Retrouver les définitions</summary>\n"
            f"{grid}\n</details>"
        )
    else:
        definitions_html = grid

    return f"{theory_html}\n\n{definitions_html}"


_EXERCISE_BLOCK_RE = re.compile(
    r"<details>\s*"
    r"<summary>Exercice \d+ — (?P<title>.+?) \(essaie avant de regarder la correction\)</summary>\s*"
    r"(?P<instructions>.*?)\s*"
    r"<details>\s*"
    r"<summary>Voir la correction expliquée</summary>\s*"
    r"(?P<correction>.*?)\s*"
    r"</details>\s*"
    r"</details>",
    re.DOTALL,
)

_FLASH_QUESTION_RE = re.compile(
    r"\*\*Question\s*:\*\*\s*(?P<question>.+?)\n\n"
    r"\*\*Corrigé expliqué\s*:\*\*\s*(?P<correction>.+)",
    re.DOTALL,
)

_WHY_CORRECT_RE = re.compile(r"\n\n(Ce corrigé fonctionne parce qu.+)\Z", re.DOTALL)


def _why_correct_split(correction_raw: str) -> tuple[str, str]:
    """Sépare la dernière phrase « Ce corrigé fonctionne parce que... » (présente dans
    tous les corrigés FSE02-17, vérifié avant d'écrire cette fonction) du reste du
    corrigé, pour l'afficher dans son propre encadré `.jc-why-correct` (voir FSE01,
    ticket #112). Retourne (corrigé_sans_la_phrase, html_de_l_encadré_ou_chaine_vide)."""
    match = _WHY_CORRECT_RE.search(correction_raw)
    if not match:
        return correction_raw, ""
    remainder = correction_raw[: match.start()].strip()
    why_html = (
        '<div class="jc-why-correct">'
        '<span class="jc-why-correct-label">Pourquoi cette réponse est correcte</span>'
        f"<p>{_inline_md_to_html(match.group(1).strip())}</p>"
        "</div>"
    )
    return remainder, why_html


def _exercise_card_html(number: int, title: str, instructions_raw: str, correction_raw: str) -> str:
    instructions_html = _paragraphs_to_html(instructions_raw)
    correction_body, why_html = _why_correct_split(correction_raw)
    correction_html = _paragraphs_to_html(correction_body)
    return (
        f'<div class="jc-exercise-card">\n'
        f'<div class="jc-exercise-card-header">'
        f'<span class="jc-exercise-number" aria-hidden="true">{number}</span>'
        f'<h4 class="jc-exercise-title">{_inline_md_to_html(title)}</h4>'
        f"</div>\n"
        f'<div class="jc-exercise-instructions">\n{instructions_html}\n</div>\n'
        f'<details class="jc-exercise-correction">\n<summary>Voir le corrigé</summary>\n'
        f'<div class="jc-exercise-correction-body">\n{correction_html}\n{why_html}\n</div>\n'
        f"</details>\n"
        f"</div>"
    )


def exercises_to_cards(text: str) -> str:
    """Convertit les exercices guidés (format `<details>` imbriqués, tickets #96-#101) en
    cartes individuelles (`.jc-exercise-card`), comme FSE01 (ticket #112) : consigne
    toujours visible, accordéon « Voir le corrigé » stylé comme un bouton (fermé par
    défaut), corrigé structuré en HTML réel. Le « Corrigé très expliqué » final (question
    flash, jamais replié dans la version originale) devient un exercice supplémentaire à
    part entière, avec sa propre carte et son propre accordéon — cohérent avec
    « corrigés fermés au chargement » appliqué partout. Voir
    `docs/components/ExerciseStepCard.md`."""
    cards: list[str] = []
    number = 0
    for match in _EXERCISE_BLOCK_RE.finditer(text):
        number += 1
        cards.append(
            _exercise_card_html(
                number,
                match.group("title").strip(),
                match.group("instructions").strip(),
                match.group("correction").strip(),
            )
        )

    flash_match = _FLASH_QUESTION_RE.search(text)
    if flash_match:
        number += 1
        question = flash_match.group("question").strip().strip("«»\" ")
        cards.append(
            _exercise_card_html(
                number,
                "Question flash",
                question,
                flash_match.group("correction").strip(),
            )
        )

    return "\n\n".join(cards)


def pieges_to_blockquotes(text: str) -> str:
    """Convertit chaque puce de premier niveau en citation Markdown (`> ...`), reconnue
    automatiquement comme WarningCard par `design_system.js`. Les puces imbriquées (sous
    une puce de premier niveau) restent regroupées dans la même citation."""
    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            out.append("")
            out.append("> " + stripped[2:])
        elif stripped:
            out.append("> " + stripped if out and out[-1].startswith(">") else stripped)
        else:
            out.append("")
    return "\n".join(out).strip("\n")


def build_course_sections(code: str, markdown: str) -> list[tuple[str, str]]:
    """Découpe le Markdown d'un cours FSE02-FSE16 (format tickets #96-#101) en blocs
    titrés — voir la docstring du module pour le détail des transformations."""
    sections = parse_numbered_sections(markdown)
    out: list[tuple[str, str]] = [
        (f"{code} — Présentation et objectifs", fix_list_blank_lines(sections[1])),
        (
            f"{code} — Théorie : notions et définitions",
            theory_and_definitions_to_cards(sections[2], sections[3]),
        ),
        (f"{code} — Méthode", fix_list_blank_lines(sections[4])),
        (
            f"{code} — Exemples commentés",
            analyse_commentee_to_decrypt(
                exemple_headers_to_titles(fix_list_blank_lines(sections[5]))
            ),
        ),
        (
            f"{code} — Comparer pour ne pas confondre",
            mauvaises_bonnes_to_comparegrid(sections[6])
            + "\n\n"
            + pieges_to_blockquotes(sections[7]),
        ),
        (
            f"{code} — Exercices guidés",
            exercises_to_cards(sections[8] + "\n\n" + sections[9]),
        ),
        (f"{code} — Fiche mémo", fix_list_blank_lines(sections[10])),
    ]
    if 11 in sections:
        out.append(
            (f"{code} — Sources officielles vérifiées", fix_list_blank_lines(sections[11]))
        )
    return out

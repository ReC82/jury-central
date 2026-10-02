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
            fix_list_blank_lines(sections[2] + "\n\n" + sections[3]),
        ),
        (f"{code} — Méthode", fix_list_blank_lines(sections[4])),
        (f"{code} — Exemples commentés", fix_list_blank_lines(sections[5])),
        (
            f"{code} — Comparer pour ne pas confondre",
            mauvaises_bonnes_to_comparegrid(sections[6])
            + "\n\n"
            + pieges_to_blockquotes(sections[7]),
        ),
        (
            f"{code} — Exercices guidés",
            fix_list_blank_lines(sections[8] + "\n\n" + sections[9]),
        ),
        (f"{code} — Fiche mémo", fix_list_blank_lines(sections[10])),
    ]
    if 11 in sections:
        out.append(
            (f"{code} — Sources officielles vérifiées", fix_list_blank_lines(sections[11]))
        )
    return out

"""Séquence finale « À retenir » d'un cours (ticket #136, complément du 21/10).

Construit, pour chaque cours, une fiche de fin de chapitre structurée :
- « L'essentiel » : la synthèse déjà rédigée du cours (« À retenir pour l'examen »,
  « Fiche mémo »), reprise telle quelle ;
- « Ce que je dois savoir faire » : les compétences du plan validé (FSE, Français), les
  objectifs du mini-cours (AMPCR MC01-03) ou l'objectif du programme + la méthode courte
  du cours (AMPCR MC04-37) ;
- « Le vocabulaire à retenir » : une carte par terme (définition du cours, acronyme
  développé, équivalent anglais, repère et confusion fréquente lorsque le cours ou le
  lexique AMPCR #84 les fournit).

Règle du projet : aucune définition n'est inventée. Tout provient du contenu déjà publié
du cours, des plans (`fse_plan`, `francais_plan`, `ampcr_plan`) et du lexique AMPCR. Les
sections mémo existantes (« À retenir pour l'examen », « Vocabulaire FR / EN », « Fiche
mémo ») sont ABSORBÉES par la fiche — jamais dupliquées : leur contenu y figure en entier
(texte repris, lignes de tableau transformées en cartes, texte restant conservé dans
« Repères et méthode »). Les explications et nuances restent dans les séquences
précédentes : la fiche les complète.

Calculé à l'affichage, sans écrire en base : aucune actualisation de seed nécessaire.
"""

from __future__ import annotations

import html
import re
from collections.abc import Sequence
from dataclasses import dataclass, field

from app.card_kind import card_meta
from app.content import render_markdown
from app.v1.ampcr_plan import _OBJECTIVES_BY_CODE
from app.v1.francais_plan import get_francais_plan_by_slug
from app.v1.fse_plan import get_fse_plan_by_slug
from app.v1.lexicon import LEXICON_THEMES, LexiconEntry

MEMO_TITLE = "À retenir"
# Matières du parcours CESS P refondu (#136). Les révisions transversales MC38 et FSE17
# sont déjà des fiches de synthèse multi-cours : pas de seconde fiche par-dessus.
MEMO_MODULES = frozenset({"AMPCR", "FRANCAIS", "FSE"})
_EXCLUDED_COURSES = frozenset({"MC38", "FSE17", "C01"})

_H2 = re.compile(r"^## +(.+?)\s*$", re.MULTILINE)
_SECTION_NUMBER = re.compile(r"^\d+\.\s*")
_SUMMARY_SECTION = re.compile(r"^(à retenir|fiche mémo)", re.IGNORECASE)
_VOCAB_SECTION = re.compile(r"^vocabulaire( à connaître)? ?(fr ?/ ?en|français ?/ ?anglais)", re.IGNORECASE)
_DEFINITION_SECTION = re.compile(r"^définitions (essentielles|importantes)", re.IGNORECASE)
_METHOD_SECTION = re.compile(r"^procédure / méthode", re.IGNORECASE)
_ACRONYM = re.compile(r"\b[A-Z][A-Z0-9]{1,}(?:-[A-Z0-9]+)?\b")


@dataclass
class VocabCard:
    term: str
    definition_html: str = ""
    expansion: str = ""
    english: str = ""
    landmark: str = ""
    confusion_html: str = ""
    example_html: str = ""

    @property
    def has_definition(self) -> bool:
        return bool(self.definition_html)

    def keys(self) -> set[str]:
        keys = {_norm(self.term), _norm(_strip_paren(self.term))}
        keys |= set(_ACRONYM.findall(self.term + " " + self.expansion))
        return {k for k in keys if k}


@dataclass
class CourseMemo:
    title: str
    summary_html: str = ""
    skills: list[str] = field(default_factory=list)
    objective: str = ""
    method_title: str = ""
    method_steps: list[str] = field(default_factory=list)
    vocabulary: list[VocabCard] = field(default_factory=list)
    notes_html: str = ""

    @property
    def definitions(self) -> list[VocabCard]:
        return [c for c in self.vocabulary if c.has_definition]

    @property
    def pairs(self) -> list[VocabCard]:
        """Équivalents français/anglais sans définition dans le cours : affichés en liste
        compacte, jamais complétés par une définition inventée."""
        return [c for c in self.vocabulary if not c.has_definition]
    # Blocs (id) et sections h2 (id du bloc, titre) repris par la fiche : retirés de
    # l'affichage normal pour ne pas créer de doublon.
    absorbed_block_ids: set[int] = field(default_factory=set)
    absorbed_sections: dict[int, set[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class BlockSource:
    id: int
    title: str
    content: str


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", text)).strip().lower()


def _strip_paren(text: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", " ", text).strip()


def _section_name(title: str) -> str:
    return _SECTION_NUMBER.sub("", title.strip())


def split_h2(markdown: str) -> list[tuple[str | None, str]]:
    """Découpe un markdown en (titre h2 ou None pour le préambule, texte complet)."""
    parts: list[tuple[str | None, str]] = []
    matches = list(_H2.finditer(markdown))
    start = matches[0].start() if matches else len(markdown)
    if markdown[:start].strip():
        parts.append((None, markdown[:start]))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        parts.append((match.group(1), markdown[match.start():end]))
    return parts


def _body(section_text: str) -> str:
    return section_text.split("\n", 1)[1] if "\n" in section_text else ""


def strip_sections(markdown: str, titles: set[str]) -> str:
    return "".join(text for title, text in split_h2(markdown) if title not in titles)


def _demote_headings(html_text: str) -> str:
    """Les sous-titres de la fiche ne doivent jamais créer une nouvelle séquence (h2)."""
    html_text = re.sub(r"<(/?)h[12]\b", r"<\1h4", html_text)
    return re.sub(r"<(/?)h3\b", r"<\1h4", html_text)


# --- Tableaux de vocabulaire ----------------------------------------------------------


def _split_tables(markdown: str) -> tuple[list[tuple[str, str]], str]:
    """Extrait les lignes (FR, EN) des tableaux à deux colonnes ; renvoie aussi le texte
    restant (sans les tableaux), pour qu'aucune phrase du cours ne soit perdue."""
    rows: list[tuple[str, str]] = []
    rest: list[str] = []
    in_table = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not in_table:
                in_table = True  # ligne d'en-tête
                continue
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            if len(cells) >= 2:
                rows.append((cells[0], cells[1]))
            continue
        in_table = False
        rest.append(line)
    return rows, "\n".join(rest)


def _capitalize(fragment: str) -> str:
    """Majuscule initiale d'un fragment (« bloc d'alimentation… » → « Bloc… »)."""
    return re.sub(r"^((?:<[^>]+>)*)([a-zà-ÿ])", lambda m: m.group(1) + m.group(2).upper(), fragment)


def _redundant(extra: str, definition_html: str) -> bool:
    """Un repère du lexique qui ne fait que répéter la définition n'apporte rien."""
    words = set(re.findall(r"\w{4,}", _norm(extra)))
    defined = set(re.findall(r"\w{4,}", _norm(re.sub(r"<[^>]+>", " ", definition_html))))
    return bool(words) and len(words & defined) / len(words) >= 0.6


def _inline(markdown: str) -> str:
    rendered = render_markdown(markdown).strip()
    match = re.fullmatch(r"<p>(.*)</p>", rendered, re.DOTALL)
    return match.group(1) if match else rendered


# --- Définitions -----------------------------------------------------------------------

_MD_DEFINITION = re.compile(
    r"^\*\*(?P<term>[^*]+)\*\*\s*(?:\((?P<exp>[^)]*)\))?\s*:\s*(?P<def>.+)$", re.DOTALL
)
_HTML_DEFINITION = re.compile(r'<div class="jc-definition(?:\s[^"]*)?">', re.IGNORECASE)


def _markdown_bullets(markdown: str) -> list[str]:
    bullets: list[str] = []
    for line in markdown.splitlines():
        if re.match(r"^\s*[-*] ", line):
            bullets.append(re.sub(r"^\s*[-*] ", "", line).strip())
        elif bullets and line.startswith("  ") and line.strip():
            bullets[-1] += " " + line.strip()
        elif not line.strip() and bullets:
            bullets.append("")
    return [b for b in bullets if b]


def parse_markdown_definitions(markdown: str) -> list[VocabCard]:
    cards = []
    for bullet in _markdown_bullets(markdown):
        match = _MD_DEFINITION.match(bullet)
        if not match:
            continue
        cards.append(
            VocabCard(
                term=match.group("term").strip(),
                expansion=(match.group("exp") or "").strip(),
                definition_html=_capitalize(_inline(match.group("def").strip())),
            )
        )
    return cards


def _html_text(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def parse_html_definitions(content: str) -> list[VocabCard]:
    cards = []
    pieces = _HTML_DEFINITION.split(content)[1:]
    for piece in pieces:
        term = re.search(r'class="jc-definition-term">(.*?)</span>', piece, re.DOTALL)
        body = re.search(r'class="jc-definition-body">(.*?)</p>', piece, re.DOTALL)
        if not term or not body:
            continue
        example = re.search(r'class="jc-definition-example">(.*?)</p>', piece, re.DOTALL)
        definition = body.group(1).strip()
        cards.append(
            VocabCard(
                term=_html_text(term.group(1)),
                definition_html=_capitalize(definition),
                example_html=example.group(1).strip() if example else "",
            )
        )
    return cards


# --- Enrichissements -------------------------------------------------------------------


def _row_acronyms(*cells: str) -> set[str]:
    return set(_ACRONYM.findall(" ".join(cells)))


def _merge_vocab_rows(cards: list[VocabCard], rows: list[tuple[str, str]]) -> None:
    for fr, en in rows:
        fr_plain, en_plain = _norm(fr), _norm(en)
        acronyms = _row_acronyms(fr, en)
        target = None
        for card in cards:
            keys = card.keys()
            if fr_plain in keys or _norm(_strip_paren(fr)) in keys or (acronyms & keys):
                target = card
                break
        if target is None:
            target = VocabCard(term=re.sub(r"[*_]", "", fr).strip())
            cards.append(target)
        english = _inline(en)
        current = _norm(re.sub(r"<[^>]+>", "", target.english))
        if not target.english or current in en_plain:
            target.english = english
        elif en_plain not in current:
            target.english += " · " + english


def _lexicon_for(course_code: str) -> dict[str, LexiconEntry]:
    entries: dict[str, LexiconEntry] = {}
    for theme in LEXICON_THEMES:
        for entry in theme.entries:
            if course_code in entry.mc_codes:
                entries.setdefault(entry.acronym, entry)
    return entries


def _apply_lexicon(cards: list[VocabCard], course_code: str) -> None:
    lexicon = _lexicon_for(course_code)
    if not lexicon:
        return
    for card in cards:
        found = card.keys() | _row_acronyms(re.sub(r"<[^>]+>", "", card.english))
        entry = next((lexicon[a] for a in sorted(found) if a in lexicon), None)
        if entry is None:
            continue
        if not card.expansion and entry.english:
            card.expansion = entry.english
        if not card.definition_html:
            card.definition_html = html.escape(entry.definition)
        if not card.landmark and not _redundant(entry.context, card.definition_html):
            card.landmark = entry.context
        if not card.confusion_html and entry.confusion:
            card.confusion_html = html.escape(entry.confusion)


_CONFUSION = re.compile(r"^>\s*\*\*(?P<title>[^*]+)\*\*\s*:?\s*(?P<text>.*)$")


def _apply_confusions(cards: list[VocabCard], markdown: str) -> None:
    """Rattache une confusion du cours (« > **Confondre X et Y** : … ») au premier terme
    qu'elle nomme — chaque confusion n'est affichée qu'une fois."""
    for line in markdown.splitlines():
        match = _CONFUSION.match(line.strip())
        if not match:
            continue
        title = match.group("title").strip()
        haystack = _norm(title)
        # Seules les confusions explicites (« Confondre X et Y ») sont rattachées à un
        # terme ; les autres erreurs de raisonnement restent dans « Comparer ».
        if not haystack.startswith("confondre"):
            continue
        for card in cards:
            term = _norm(_strip_paren(card.term))
            if card.confusion_html or len(term) < 3:
                continue
            if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", haystack):
                text = match.group("text").strip()
                card.confusion_html = "<strong>" + html.escape(title) + "</strong>" + (
                    " : " + _inline(text) if text else ""
                )
                break


def _parse_method(section_body: str) -> tuple[str, list[str]]:
    text = re.sub(r"\s+", " ", section_body).strip()
    if "(1)" not in text:
        return "", []
    head, _, steps_text = text.partition("(1)")
    steps = [s.strip(" ;.") for s in re.split(r"\(\d+\)", "(1)" + steps_text) if s.strip(" ;.")]
    return head.strip(" :"), [_capitalize(_inline(s)) for s in steps]


def _plan_objectives(markdown: str) -> list[str]:
    for title, text in split_h2(markdown):
        if title and title.lower().startswith("objectifs"):
            return [_inline(b.rstrip(" ;.")) for b in _markdown_bullets(_body(text))]
    return []


# --- Construction ----------------------------------------------------------------------


def build_course_memo(
    module_code: str,
    uaa_code: str,
    uaa_slug: str,
    uaa_title: str,
    blocks: Sequence[BlockSource],
) -> CourseMemo | None:
    """Fiche « À retenir » d'un cours, ou None si le cours n'a aucune synthèse publiée
    (révisions transversales MC38/FSE17, texte pilote C01, Mathématiques : inchangés)."""
    if module_code not in MEMO_MODULES or uaa_code in _EXCLUDED_COURSES:
        return None
    memo = CourseMemo(title=uaa_title)
    # Un cours d'un seul bloc (AMPCR MC04-37, Français) porte ses sections mémo en h2 ;
    # dans un cours en plusieurs cartes (MC01-03), un « À retenir » interne à une carte
    # reste à sa place : il fait partie de la leçon de cette carte.
    single_body = len(blocks) == 1
    summaries: list[str] = []
    vocab_rows: list[tuple[str, str]] = []
    notes: list[str] = []
    cards: list[VocabCard] = []
    confusion_sources: list[str] = []

    for block in blocks:
        name = _section_name(block.title.split(" — ", 1)[-1] if module_code == "FSE" else block.title)
        if module_code == "FSE" and _SUMMARY_SECTION.match(name):
            summaries.append(block.content)
            memo.absorbed_block_ids.add(block.id)
            continue
        if module_code == "FSE":
            cards.extend(parse_html_definitions(block.content))
            if name.lower().startswith("comparer"):
                confusion_sources.append(block.content)
            continue
        if _SUMMARY_SECTION.match(name):
            # Fiche mémo autonome (AMPCR MC01-03) : son tableau de vocabulaire rejoint
            # les cartes, le reste (composants, chemin, pièges) reste en « L'essentiel ».
            kept = []
            for title, text in split_h2(block.content):
                if title and _VOCAB_SECTION.match(title):
                    rows, _rest = _split_tables(_body(text))
                    vocab_rows.extend(rows)
                elif title is None:
                    kept.append(re.sub(r"^# .*\n", "", text.lstrip()))
                else:
                    kept.append(text)
            summaries.append("".join(kept))
            memo.absorbed_block_ids.add(block.id)
            continue
        if _VOCAB_SECTION.match(name):
            rows, rest = _split_tables(block.content)
            vocab_rows.extend(rows)
            notes.append(rest)
            memo.absorbed_block_ids.add(block.id)
            continue
        for title, text in split_h2(block.content):
            if title is None:
                continue
            section = _section_name(title)
            if not single_body and (_SUMMARY_SECTION.match(section) or _VOCAB_SECTION.match(section)):
                continue
            if _SUMMARY_SECTION.match(section):
                summaries.append(_body(text))
                memo.absorbed_sections.setdefault(block.id, set()).add(title)
            elif _VOCAB_SECTION.match(section):
                rows, rest = _split_tables(_body(text))
                vocab_rows.extend(rows)
                notes.append(rest)
                memo.absorbed_sections.setdefault(block.id, set()).add(title)
            elif _DEFINITION_SECTION.match(section):
                cards.extend(parse_markdown_definitions(_body(text)))
            elif _METHOD_SECTION.match(section) and not memo.method_steps:
                memo.method_title, memo.method_steps = _parse_method(_body(text))
        if block.title.lower().startswith("plan du mini-cours"):
            memo.skills = _plan_objectives(block.content)

    if not any(s.strip() for s in summaries):
        return None

    memo.summary_html = _demote_headings(
        "".join(render_markdown(s.strip()) for s in summaries if s.strip())
    )
    _merge_vocab_rows(cards, vocab_rows)
    if module_code == "AMPCR":
        _apply_lexicon(cards, uaa_code)
    for source in confusion_sources:
        _apply_confusions(cards, source)
    seen: set[str] = set()
    for card in cards:
        key = _norm(card.term)
        if key not in seen:
            seen.add(key)
            memo.vocabulary.append(card)

    notes_md = "\n\n".join(n.strip() for n in notes if n.strip())
    memo.notes_html = _demote_headings(render_markdown(notes_md)) if notes_md else ""

    if module_code == "FSE":
        plan = get_fse_plan_by_slug(uaa_slug)
        memo.skills = list(plan.competencies) if plan else []
    elif module_code == "FRANCAIS":
        plan = get_francais_plan_by_slug(uaa_slug)
        memo.skills = list(plan.competencies or ()) if plan else []
    elif module_code == "AMPCR" and not memo.skills:
        memo.objective = _OBJECTIVES_BY_CODE.get(uaa_code, "")
    return memo


def apply_course_memo(
    module_code: str,
    uaa_code: str,
    uaa_slug: str,
    uaa_title: str,
    course_blocks: Sequence,
    rendered_blocks: list[dict],
) -> CourseMemo | None:
    """Remplace, dans le rendu du cours, les sections mémo existantes par la séquence
    finale « À retenir ». `course_blocks` : blocs ORM de l'espace Cours (lecture seule —
    jamais modifiés, le texte allégé est recalculé à part)."""
    sources = [
        BlockSource(b.id, b.title, b.content)
        for b in course_blocks
        if b.is_published and b.type.value == "markdown"
    ]
    memo = build_course_memo(module_code, uaa_code, uaa_slug, uaa_title, sources)
    if memo is None:
        return None
    kept: list[dict] = []
    for item in rendered_blocks:
        block = item.get("block")
        if block is not None and block.id in memo.absorbed_block_ids:
            continue
        if block is not None and block.id in memo.absorbed_sections:
            item["html"] = render_markdown(
                strip_sections(block.content, memo.absorbed_sections[block.id])
            )
        kept.append(item)
    single = [i for i in kept if i.get("block") is not None and i["block"].id in memo.absorbed_sections]
    if len(kept) == 1 and single:
        # Cours d'un seul bloc : la fiche suit le texte, dans le même conteneur, pour
        # devenir la dernière séquence (découpage par titres h2).
        single[0]["memo"] = memo
    else:
        kept.append(
            {
                "block": None,
                "quiz_run": None,
                "memo_card": memo,
                "card": card_meta("summary"),
            }
        )
    rendered_blocks[:] = kept
    return memo

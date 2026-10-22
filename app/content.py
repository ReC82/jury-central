import re

import markdown as markdown_lib

_YOUTUBE_PATTERNS = [
    r"youtu\.be/([\w-]{11})",
    r"youtube\.com/watch\?v=([\w-]{11})",
    r"youtube\.com/embed/([\w-]{11})",
]


def render_markdown(text: str) -> str:
    return markdown_lib.markdown(text, extensions=["fenced_code", "tables"])


# Balises d'un texte suivi (ticket #148). Tout autre élément — tableau, image, schéma,
# grille/carte en <div>, titre de section <h1>/<h2> d'un cours en un seul bloc — signale
# un contenu qui a besoin de la pleine largeur de la carte.
_TEXT_ONLY_TAGS = frozenset(
    {"p", "ul", "ol", "li", "strong", "em", "b", "i", "a", "br", "code", "span",
     "h3", "h4", "h5", "blockquote", "sup", "sub", "abbr", "small"}
)
_TAG_RE = re.compile(r"<\s*([a-zA-Z][a-zA-Z0-9]*)")


def is_text_only_html(html: str) -> bool:
    """Vrai si le HTML rendu d'un bloc n'est que du texte suivi (paragraphes, listes,
    mise en évidence) : sa carte peut alors prendre une largeur de lecture confortable
    (`.jc-card--reading`) au lieu de s'étirer sur toute la colonne du cours."""
    tags = {t.lower() for t in _TAG_RE.findall(html or "")}
    return bool(tags) and tags <= _TEXT_ONLY_TAGS


def extract_youtube_id(value: str) -> str | None:
    value = value.strip()
    for pattern in _YOUTUBE_PATTERNS:
        match = re.search(pattern, value)
        if match:
            return match.group(1)
    if re.fullmatch(r"[\w-]{11}", value):
        return value
    return None

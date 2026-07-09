import re

import markdown as markdown_lib

_YOUTUBE_PATTERNS = [
    r"youtu\.be/([\w-]{11})",
    r"youtube\.com/watch\?v=([\w-]{11})",
    r"youtube\.com/embed/([\w-]{11})",
]


def render_markdown(text: str) -> str:
    return markdown_lib.markdown(text, extensions=["fenced_code", "tables"])


def extract_youtube_id(value: str) -> str | None:
    value = value.strip()
    for pattern in _YOUTUBE_PATTERNS:
        match = re.search(pattern, value)
        if match:
            return match.group(1)
    if re.fullmatch(r"[\w-]{11}", value):
        return value
    return None

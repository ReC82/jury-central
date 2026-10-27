"""Fiches de dépannage AMPCR Pratique écrite (ticket #302) : un manuel opérationnel de diagnostic
et d'intervention par module du programme (6 fiches), consultable sur le site, téléchargeable en
HTML autonome et imprimable en A4.

Le contenu est versionné en fragments HTML dans `app/v1/ampcr_fiches/f<N>/` (concaténés par ordre
de nom de fichier). Une fiche n'est proposée que si ses fragments sont présents : elles sont livrées
une par une. Aucune donnée en base.
"""

import html
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.v1 import ampcr_pratique_plan as plan

CONTENT_DIR = Path(__file__).parent / "ampcr_fiches"
CSS_PATH = Path(__file__).resolve().parent.parent / "static" / "css" / "fiches.css"
FICHES_URL = f"{plan.PRACTICAL_PATH_URL}/fiches"
SITE_URL = "https://jury-central.lodylands.com"


@dataclass(frozen=True)
class Fiche:
    number: int
    title: str
    module_key: str  # module du parcours installé à la fin duquel la fiche est proposée
    courses: str  # cours couverts (programme du propriétaire, 6 modules)

    @property
    def url(self) -> str:
        return f"{FICHES_URL}/{self.number}"

    @property
    def download_url(self) -> str:
        return f"{self.url}/telecharger"

    @property
    def filename(self) -> str:
        return f"fiche-{self.number}-ampcr-pratique-depannage.html"


FICHES: tuple[Fiche, ...] = (
    Fiche(1, "Maintenance matérielle : diagnostic et intervention", "P1", "PR01–PR06 · EX01"),
    Fiche(2, "Systèmes Windows et Linux : diagnostic et dépannage", "P2", "PR07–PR12 · EX02"),
    Fiche(3, "Câblage cuivre, coaxial, fibre et installation physique", "P3", "PR13–PR18 · EX03"),
    Fiche(4, "Réseau : adressage, services, partages, Wi-Fi et dépannage", "P4", "PR19–PR25 · EX04"),
    Fiche(5, "Méthode d'intervention professionnelle", "P5", "PR26–PR29"),
    Fiche(6, "Synthèse : réussir l'épreuve pratique écrite, dossiers intégrés", "P5", "PR30 · EX05 · EX06"),
)
FICHES_BY_NUMBER = {f.number: f for f in FICHES}


def _fragments(number: int) -> list[Path]:
    return sorted((CONTENT_DIR / f"f{number}").glob("*.html"))


def is_available(number: int) -> bool:
    return number in FICHES_BY_NUMBER and bool(_fragments(number))


def available_fiches() -> list[Fiche]:
    return [f for f in FICHES if is_available(f.number)]


def fiches_for_module(module_key: str) -> list[Fiche]:
    return [f for f in FICHES if f.module_key == module_key]


_TABLE_RE = re.compile(r'<table class="fx-table">(.*?)</table>', re.DOTALL)
_TH_RE = re.compile(r"<th[^>]*>(.*?)</th>", re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")


def _stack_tables(source: str) -> str:
    """Matrices de 4 colonnes ou plus : étiquette de colonne sur chaque cellule, pour l'affichage
    en cartes sur mobile (voir `.fx-stack` dans fiches.css). Sans effet à l'impression."""

    def repl(match: re.Match) -> str:
        body = match.group(1)
        head = re.search(r"<thead>(.*?)</thead>", body, re.DOTALL)
        labels = [html.escape(_TAG_RE.sub("", h).strip(), quote=True) for h in _TH_RE.findall(head.group(1))] if head else []
        if len(labels) < 4:
            return match.group(0)

        def row(tr: re.Match) -> str:
            cells = iter(labels)
            return re.sub(r"<td(?=[\s>])", lambda _m: f'<td data-label="{next(cells, "")}"', tr.group(0))

        body = re.sub(r"<tbody>.*?</tbody>",
                      lambda tb: re.sub(r"<tr[\s>].*?</tr>", row, tb.group(0), flags=re.DOTALL), body, flags=re.DOTALL)
        return f'<table class="fx-table fx-stack">{body}</table>'

    return _TABLE_RE.sub(repl, source)


@lru_cache(maxsize=8)
def _content_cached(number: int, stamp: tuple) -> str:
    return _stack_tables("\n".join(p.read_text(encoding="utf-8") for p in _fragments(number)))


def content(number: int) -> str:
    stamp = tuple((p.name, p.stat().st_mtime_ns) for p in _fragments(number))
    return _content_cached(number, stamp)


def css() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


def standalone_content(number: int) -> str:
    """Contenu pour le fichier autonome : liens vers la même fiche → ancres locales ; autres liens
    du site → adresse complète (le fichier est lu hors connexion, hors du site)."""
    source = content(number)
    source = re.sub(rf'href="{re.escape(FICHES_URL)}/{number}#', 'href="#', source)
    return re.sub(r'href="/(?!/)', f'href="{SITE_URL}/', source)

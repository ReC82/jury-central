"""Ticket #192 — référence officielle versionnée (PDF des consignes pratique AMPCR 2026-2027/1).

Le PDF doit être présent dans le dépôt, identique à l'empreinte de `OFFICIAL_SOURCE`, avec
ses 6 pages, et chaque exigence officielle de la matrice doit figurer mot pour mot dans la
transcription, à la page indiquée.
"""

import hashlib
import re
from pathlib import Path

from app.v1 import ampcr_pratique_plan as plan

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / plan.OFFICIAL_SOURCE.repo_path
REF_DIR = PDF.parent
TRANSCRIPTION = REF_DIR / "transcription.md"


def _norm(text: str) -> str:
    # Les retours à la ligne du PDF coupent parfois un mot composé (« RAM-\nROM »).
    text = re.sub(r"-\s*\n\s*", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def _pages() -> dict[int, str]:
    text = TRANSCRIPTION.read_text(encoding="utf-8")
    parts = re.split(r"^## Page (\d+)/6$", text, flags=re.MULTILINE)
    return {
        int(parts[i]): _norm(parts[i + 1].replace("```text", "").replace("```", ""))
        for i in range(1, len(parts), 2)
    }


def test_official_pdf_is_versioned_with_expected_fingerprint():
    assert plan.OFFICIAL_SOURCE.repo_path.endswith(
        "26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf"
    )
    data = PDF.read_bytes()
    assert data.startswith(b"%PDF-")
    assert hashlib.sha256(data).hexdigest() == plan.OFFICIAL_SOURCE.sha256


def test_official_pdf_has_six_pages():
    data = PDF.read_bytes()
    assert len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", data)) == plan.OFFICIAL_SOURCE.pages == 6
    pages = _pages()
    assert sorted(pages) == [1, 2, 3, 4, 5, 6]
    for number, text in pages.items():
        assert text.startswith(f"{number}/6")


def test_readme_documents_provenance_and_rights():
    readme = (REF_DIR / "README.md").read_text(encoding="utf-8")
    assert plan.OFFICIAL_SOURCE.sha256 in readme
    assert plan.OFFICIAL_SOURCE.url in readme
    assert "Droits de redistribution" in readme
    assert "transcription.md" in readme


def test_every_official_requirement_is_quoted_on_its_page():
    pages = _pages()
    official = [r for r in plan.OFFICIAL_REQUIREMENTS if r.kind == plan.KIND_OFFICIAL]
    assert len(official) == 38
    for requirement in official:
        assert _norm(requirement.text) in pages[requirement.page], requirement.id
    # 18 puces p. 5, 20 puces p. 6 : aucune puce du PDF oubliée par la matrice.
    assert pages[5].count("●") == sum(r.page == 5 for r in official) == 18
    assert pages[6].count("●") == sum(r.page == 6 for r in official) == 20


def test_day_instructions_come_from_their_page():
    pages = _pages()
    for section in plan.DAY_INSTRUCTIONS:
        for paragraph in section.paragraphs:
            # La liste « T.P. ET MÉTHODES / LABORATOIRE » du PDF est rendue sur une ligne.
            for chunk in _norm(paragraph).split(" — "):
                assert chunk in pages[section.page], (section.title, chunk)


def test_pages_link_the_versioned_copy(client):
    for url in ("/ampcr-pratique", "/ampcr-pratique/matrice"):
        response = client.get(url)
        assert response.status_code == 200
        assert plan.OFFICIAL_SOURCE_REPO_URL in response.text

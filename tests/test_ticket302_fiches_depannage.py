"""Ticket #302 : fiches de dépannage AMPCR Pratique (page, HTML autonome téléchargeable, A4)."""

from app.v1 import ampcr_fiches

FRAGMENT = """<header class="fx-head"><h1>Fiche test</h1></header>
<section class="fx-sec" id="f1-matrice"><h2>2. Matrice</h2>
<div class="fx-table-wrap"><table class="fx-table"><thead><tr><th>Symptôme</th><th>Causes</th><th>Test</th>
<th>Correction</th></tr></thead><tbody><tr><td>Écran noir</td><td>RAM</td><td>POST</td><td>Réinsérer</td></tr>
</tbody></table></div>
<p><a href="/ampcr-pratique/fiches/1#f1-matrice">ici</a> <a class="fx-ref" href="/ampcr-pratique/fiches/4#f4-dhcp">F4</a></p>
</section>"""


def _content(tmp_path, monkeypatch):
    (tmp_path / "f1").mkdir()
    (tmp_path / "f1" / "00-test.html").write_text(FRAGMENT, encoding="utf-8")
    monkeypatch.setattr(ampcr_fiches, "CONTENT_DIR", tmp_path)


def test_only_written_fiches_are_offered(client, tmp_path, monkeypatch):
    _content(tmp_path, monkeypatch)
    assert [f.number for f in ampcr_fiches.available_fiches()] == [1]
    assert client.get("/ampcr-pratique/fiches/2").status_code == 404
    home = client.get("/ampcr-pratique").text
    assert "/ampcr-pratique/fiches/1" in home and 'id="fiche-P1"' in home
    assert "En cours de rédaction" in client.get("/ampcr-pratique/fiches").text


def test_fiche_page_has_download_print_and_mobile_tables(client, tmp_path, monkeypatch):
    _content(tmp_path, monkeypatch)
    page = client.get("/ampcr-pratique/fiches/1")
    assert page.status_code == 200
    assert "Télécharger HTML" in page.text and "window.print()" in page.text
    assert 'class="fx-table fx-stack"' in page.text and 'data-label="Correction"' in page.text
    assert "@page { size: A4" in page.text


def test_download_is_a_standalone_html_file(client, tmp_path, monkeypatch):
    _content(tmp_path, monkeypatch)
    response = client.get("/ampcr-pratique/fiches/1/telecharger")
    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    body = response.text
    assert body.startswith("<!doctype html>") and "<style>" in body
    assert "<link" not in body and "<script" not in body
    assert 'href="#f1-matrice"' in body
    assert 'href="https://jury-central.lodylands.com/ampcr-pratique/fiches/4#f4-dhcp"' in body

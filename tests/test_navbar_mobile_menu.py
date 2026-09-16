"""Non-régression du ticket #18 : bouton hamburger mobile inerte.

Cause : l'attribut `integrity` (Subresource Integrity) du bundle JS Bootstrap chargé par
CDN dans `app/templates/base.html` ne correspondait pas au contenu réel du fichier. Un
navigateur qui détecte cet écart bloque silencieusement l'exécution du script (aucune
erreur visible pour l'utilisateur, uniquement dans la console) : le CSS Bootstrap (chargé
séparément, intégrité correcte) affiche bien le bouton hamburger, mais son comportement
(`data-bs-toggle="collapse"`) ne s'active jamais, faute de JS Bootstrap exécuté.

Le hash correct a été recalculé le 2026-09-16 par téléchargement direct du fichier exact
servi par l'URL versionnée (`bootstrap@5.3.3`, immuable) :
    curl -sL -o bootstrap.bundle.min.js \
        https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js
    openssl dgst -sha384 -binary bootstrap.bundle.min.js | openssl base64 -A

Ce test ne refait pas cet appel réseau (déterministe, rapide, ne dépend pas d'un accès
Internet en CI) : il fige le hash correct connu et vérifie que le template ne régresse
pas. Si la version de Bootstrap est mise à jour, ce hash doit être recalculé de la même
façon et cette constante mise à jour en conséquence.
"""

import re
from pathlib import Path

BASE_HTML = (
    Path(__file__).resolve().parent.parent / "app" / "templates" / "base.html"
).read_text(encoding="utf-8")

# Recalculé le 2026-09-16 depuis le fichier réel servi par l'URL exacte ci-dessous — voir
# le docstring du module pour la commande utilisée.
BOOTSTRAP_JS_URL = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
BOOTSTRAP_JS_INTEGRITY = (
    "sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
)


def test_bootstrap_bundle_script_tag_has_the_correct_integrity_hash():
    """La cause exacte du bug #18 : régression si quelqu'un retype/modifie ce hash sans
    le recalculer depuis le fichier réel."""
    pattern = (
        r'<script\s+src="'
        + re.escape(BOOTSTRAP_JS_URL)
        + r'"\s+integrity="([^"]+)"'
    )
    match = re.search(pattern, BASE_HTML)
    assert match is not None, "balise <script> du bundle Bootstrap introuvable ou modifiée"
    assert match.group(1) == BOOTSTRAP_JS_INTEGRITY


def test_bootstrap_bundle_script_is_not_deferred_or_async():
    """Le bundle doit s'exécuter dès son chargement (pas de defer/async) : Bootstrap
    enregistre son gestionnaire de clic délégué sur `document` à l'exécution du script,
    avant tout clic possible sur le bouton hamburger."""
    tag_match = re.search(
        r"<script[^>]*" + re.escape(BOOTSTRAP_JS_URL) + r"[^>]*>", BASE_HTML
    )
    assert tag_match is not None
    tag = tag_match.group(0)
    assert "defer" not in tag
    assert "async" not in tag


def test_navbar_toggler_markup_matches_the_collapse_target():
    """Structure Bootstrap standard du hamburger : data-bs-toggle/data-bs-target,
    aria-controls et l'id du bloc `.collapse` doivent correspondre exactement — sinon
    Bootstrap ne trouve pas l'élément à ouvrir/fermer, même avec un JS qui s'exécute
    correctement."""
    toggler_match = re.search(
        r'<button[^>]*class="navbar-toggler"[^>]*>', BASE_HTML, re.DOTALL
    )
    assert toggler_match is not None
    toggler = toggler_match.group(0)

    assert 'data-bs-toggle="collapse"' in toggler
    target_match = re.search(r'data-bs-target="#([^"]+)"', toggler)
    controls_match = re.search(r'aria-controls="([^"]+)"', toggler)
    assert target_match is not None
    assert controls_match is not None

    target_id = target_match.group(1)
    assert target_id == controls_match.group(1)

    # L'élément collapse ciblé existe bien, avec le même id, et porte les classes
    # Bootstrap attendues (pas un second menu mobile parallèle).
    collapse_match = re.search(
        rf'<div class="collapse navbar-collapse" id="{re.escape(target_id)}">', BASE_HTML
    )
    assert collapse_match is not None


def test_only_one_navbar_toggler_and_one_collapse_target_exist():
    """Garde-fou explicite contre un contournement par un second menu mobile parallèle
    (interdit par le ticket #18) : un seul hamburger, une seule cible collapse."""
    assert BASE_HTML.count('class="navbar-toggler"') == 1
    assert BASE_HTML.count('class="collapse navbar-collapse"') == 1


def test_navbar_uses_responsive_expand_breakpoint_for_mobile_widths():
    """`navbar-expand-md` : le menu est replié (hamburger visible) sous 768px — couvre les
    trois largeurs mobiles demandées par le ticket (360/390/430px), toutes < 768px — et
    déplié (hamburger masqué) en desktop, sans code JS/CSS supplémentaire à maintenir."""
    nav_match = re.search(r'<nav class="([^"]+)"', BASE_HTML)
    assert nav_match is not None
    assert "navbar-expand-md" in nav_match.group(1)

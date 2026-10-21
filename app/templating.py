from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.database import SessionLocal

BASE_DIR = Path(__file__).resolve().parent


def _inject_current_user(request: Request) -> dict:
    """Expose `current_user` (ou `None`) ET `csrf_token` à TOUTES les pages rendues via
    `templates`, sans devoir les ajouter au contexte de chaque route une par une —
    nécessaire pour que `base.html` puisse adapter sa navigation (Connexion/Créer un
    compte vs display_name/Mon compte/Déconnexion, ticket #39) et poser le jeton CSRF du
    formulaire de déconnexion quelle que soit la page. Une route qui a déjà besoin de son
    propre `csrf_token` explicite (register/login/account) peut toujours le passer dans
    son propre contexte — mêmes valeur et session, aucun conflit (voir
    `app.v1.auth.get_or_create_csrf_token`, idempotent).

    Import différé (évite tout risque de cycle au chargement du module : `app.v1.auth`
    n'importe jamais `app.templating`, mais garder ce module, très largement importé,
    aussi peu couplé que possible au reste de l'application reste plus sûr)."""
    from app.v1.auth import get_current_user, get_or_create_csrf_token

    db = SessionLocal()
    try:
        return {
            "current_user": get_current_user(request, db),
            "csrf_token": get_or_create_csrf_token(request),
        }
    finally:
        db.close()


templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates"), context_processors=[_inject_current_user]
)


def static_exists(path: str) -> bool:
    """Ticket #136 : une illustration générée n'est affichée que si son fichier existe
    réellement — sinon le template retombe sur un rendu de secours (icône), jamais une
    image cassée."""
    return (BASE_DIR / "static" / path).is_file()


templates.env.globals["static_exists"] = static_exists


def _register_document_layouts() -> None:
    """Ticket #149 : composants des documents sources (`_document_layouts.html`)."""
    from app.v1 import document_layouts

    templates.env.globals["doc_layout"] = document_layouts.resolve_layout
    templates.env.globals["doc_heading"] = document_layouts.display_heading
    templates.env.globals["doc_focus"] = document_layouts.focus_numbers
    templates.env.globals["doc_generic"] = document_layouts.generic_parts
    templates.env.globals["course_card_html"] = document_layouts.course_card_html


_register_document_layouts()

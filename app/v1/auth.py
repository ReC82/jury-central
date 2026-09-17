"""Authentification utilisateur V1 (ticket #39).

Voir `docs/auth_v1.md` pour l'architecture complète (audit préalable, choix retenus,
routes protégées) — ce module contient l'implémentation : hachage de mot de passe,
session web, CSRF, et les dépendances FastAPI `current_user`/`require_user`/
`require_role`.

Ne construit ni la vérification d'email ni la réinitialisation de mot de passe (hors
périmètre du ticket #39) ni de rôle spécifique par interface (student reste la seule
expérience utilisateur construite ici — teacher/admin/author sont reconnus par le modèle
et les helpers de rôle, sans interface dédiée).

Distinct de `app.auth` (HTTP Basic-like pour l'admin existant, table `v1_users` non
concernée) et de `app.v1.models.QuestionnaireSession` (état d'un questionnaire, pas une
session web) — deux mécanismes différents, jamais mélangés ici malgré le nom proche."""

import secrets
from datetime import UTC, datetime
from urllib.parse import urlsplit

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.v1.models import User, UserRole

_password_hasher = PasswordHasher()

# Choix V1, documenté dans docs/auth_v1.md : pas de règle de complexité au-delà d'une
# longueur minimale raisonnable — ne pas imposer une politique non demandée par le ticket.
MIN_PASSWORD_LENGTH = 8

SESSION_USER_ID_KEY = "v1_user_id"
SESSION_CSRF_KEY = "v1_csrf_token"


class RegistrationError(ValueError):
    """Inscription refusée (email déjà utilisé, mot de passe invalide...) — message déjà
    adapté à l'affichage utilisateur (jamais une trace interne)."""


# --- Mots de passe -------------------------------------------------------------------------


def hash_password(password: str) -> str:
    """Argon2id (bibliothèque `argon2-cffi`, paramètres par défaut recommandés du
    projet — jamais d'algorithme réimplémenté ici). La chaîne retournée encode
    l'algorithme, les paramètres et le sel : aucune colonne de sel séparée nécessaire."""
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Comparaison en temps constant assurée par `argon2-cffi` — jamais une comparaison
    `==` sur les hachages ici. Toute exception de la bibliothèque (hash malformé, mismatch)
    se traduit uniformément par `False`, jamais par une exception qui remonterait au
    client ou un message distinguant la cause."""
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False


# --- Email ----------------------------------------------------------------------------------


def normalize_email(email: str) -> str:
    """Minuscules + espaces superflus retirés — stocké tel quel dans `User.email` (pas
    de colonne `email_normalized` séparée, voir `app.v1.models.User`, docstring)."""
    return email.strip().lower()


# --- Inscription / authentification --------------------------------------------------------


def register_user(
    db: Session, *, email: str, password: str, password_confirm: str, display_name: str | None = None
) -> User:
    """Point d'entrée UNIQUE pour créer un utilisateur V1 avec mot de passe — garantit
    qu'aucun mot de passe en clair n'est jamais persisté ailleurs. Valeurs automatiques :
    role=student, plan=free, is_active=true (jamais déductibles d'une entrée utilisateur)."""
    normalized = normalize_email(email)
    if not normalized or "@" not in normalized:
        raise RegistrationError("Adresse email invalide.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise RegistrationError(
            f"Le mot de passe doit contenir au moins {MIN_PASSWORD_LENGTH} caractères."
        )
    if password != password_confirm:
        raise RegistrationError("Les mots de passe ne correspondent pas.")

    existing = db.query(User).filter_by(email=normalized).one_or_none()
    if existing is not None:
        raise RegistrationError("Cette adresse email est déjà utilisée.")

    user = User(
        email=normalized,
        display_name=(display_name or "").strip() or None,
        role=UserRole.STUDENT,
        password_hash=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> User | None:
    """Retourne l'utilisateur si email + mot de passe correspondent à un compte actif,
    sinon `None` dans TOUS les cas (email inconnu, mot de passe erroné, compte inactif,
    compte sans mot de passe) — jamais de distinction observable par l'appelant, pour
    respecter « message générique en cas d'échec » / « ne pas révéler si l'email existe »
    au niveau de la route (voir `app/v1/routes.py::login_submit`)."""
    normalized = normalize_email(email)
    user = db.query(User).filter_by(email=normalized).one_or_none()
    if user is None or not user.is_active or not user.password_hash:
        # Hachage factice pour garder un temps de réponse comparable au cas normal (évite
        # qu'un email inexistant réponde perceptiblement plus vite qu'un mauvais mot de
        # passe — défense en profondeur, pas une garantie absolue sur un service web réel).
        verify_password(password, _password_hasher.hash("dummy-timing-defense"))
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# --- Session web -----------------------------------------------------------------------------


def login_user(request: Request, user: User) -> None:
    """Régénère la session (purge toute donnée précédente, y compris un éventuel jeton
    CSRF émis avant authentification) avant d'y placer l'identifiant utilisateur — limite
    la fixation de session : un jeton de session obtenu avant connexion ne doit pas rester
    valide avec les mêmes clés après authentification."""
    request.session.clear()
    request.session[SESSION_USER_ID_KEY] = user.id


def logout_user(request: Request) -> None:
    """Ne retire que les clés propres à l'authentification V1 — n'efface jamais une
    éventuelle session admin (`is_admin`/`username`, voir `app.auth`) qui coexisterait
    dans le même cookie de session."""
    request.session.pop(SESSION_USER_ID_KEY, None)


def get_current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get(SESSION_USER_ID_KEY)
    if user_id is None:
        return None
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        return None
    return user


def current_user_dependency(
    request: Request, db: Session = Depends(get_db)  # noqa: B008
) -> User | None:
    """Dépendance FastAPI : `None` si personne n'est connecté — jamais une erreur. À
    utiliser pour une page qui s'adapte (nav, contenu optionnel) sans exiger de compte."""
    return get_current_user(request, db)


def require_user(request: Request, db: Session = Depends(get_db)) -> User:  # noqa: B008
    """Dépendance FastAPI pour une PAGE HTML : exige un utilisateur connecté et actif,
    sinon redirige vers `/login?next=<chemin demandé>` (même schéma que
    `app.auth.require_admin` pour l'admin). Le `next` est construit depuis la requête
    elle-même (jamais une entrée utilisateur à cet endroit), donc toujours sûr par
    construction. Pour une route API JSON, voir `require_user_api` ci-dessous : une
    redirection 303 n'a pas de sens pour un appel `fetch()`."""
    user = get_current_user(request, db)
    if user is None:
        next_path = request.url.path
        if request.url.query:
            next_path = f"{next_path}?{request.url.query}"
        raise HTTPException(
            status_code=303, headers={"Location": f"/login?next={next_path}"}
        )
    return user


def require_user_api(request: Request, db: Session = Depends(get_db)) -> User:  # noqa: B008
    """Dépendance FastAPI pour une route API JSON (voir `app/practice.py`,
    `/api/ai/generate`, `/api/ai/correct`, `/api/editorial/{block_id}/verify`) : lève un
    401 JSON exploitable par le client (`fetch()`) au lieu d'une redirection HTML, qui
    serait silencieusement suivie et casserait le parsing JSON côté navigateur."""
    user = get_current_user(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentification requise pour cette action.")
    return user


def require_role(*roles: UserRole):
    """Fabrique une dépendance FastAPI exigeant un utilisateur connecté ET dont le rôle
    figure parmi `roles`. Aucune route ne l'utilise encore dans ce ticket (aucune
    interface teacher/admin/author construite) — prête pour les tickets suivants."""

    def _dependency(user: User = Depends(require_user)) -> User:  # noqa: B008
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Rôle insuffisant pour cette action.")
        return user

    return _dependency


def record_login(user: User) -> None:
    user.last_login_at = datetime.now(UTC)


# --- CSRF ------------------------------------------------------------------------------------
#
# Aucun mécanisme CSRF n'existe ailleurs dans ce projet à ce jour (vérifié : ni
# `app/admin.py`, ni aucun autre routeur) — ceci n'est donc pas un second système
# concurrent mais le premier, scopé aux routes de mutation ajoutées par ce ticket
# (inscription/connexion/déconnexion). Synchronizer token pattern classique, appuyé sur
# la session déjà signée par `SessionMiddleware` (`app.main`) : le jeton est stocké
# côté serveur (dans la session signée), jamais dérivable du cookie seul.


def get_or_create_csrf_token(request: Request) -> str:
    token = request.session.get(SESSION_CSRF_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        request.session[SESSION_CSRF_KEY] = token
    return token


def validate_csrf_token(request: Request, submitted_token: str | None) -> bool:
    expected = request.session.get(SESSION_CSRF_KEY)
    if not expected or not submitted_token:
        return False
    return secrets.compare_digest(expected, submitted_token)


# --- Open redirect -----------------------------------------------------------------------------


def safe_next_path(candidate: str | None, default: str = "/") -> str:
    """Ne renvoie jamais autre chose qu'un chemin local commençant par un seul `/` — un
    `next` fourni par l'utilisateur (paramètre de requête) ne doit jamais pouvoir
    rediriger vers un domaine externe (protection contre l'open redirect)."""
    if not candidate:
        return default
    if not candidate.startswith("/") or candidate.startswith("//"):
        return default
    if "\\" in candidate:
        return default
    parsed = urlsplit(candidate)
    if parsed.scheme or parsed.netloc:
        return default
    return candidate

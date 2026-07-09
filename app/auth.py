import hmac

from fastapi import HTTPException, Request

from app.config import settings


def verify_credentials(username: str, password: str) -> bool:
    correct_username = hmac.compare_digest(username, settings.admin_username)
    correct_password = hmac.compare_digest(password, settings.admin_password)
    return correct_username and correct_password


def require_admin(request: Request) -> None:
    if not request.session.get("is_admin"):
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})

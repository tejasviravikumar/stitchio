"""Shared FastAPI dependencies: database session and current user."""
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.security import AuthError, decode_supabase_token

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str | None = None


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> CurrentUser:
    s = get_settings()
    if creds is None:
        if s.dev_auth_bypass and s.environment == "dev":
            return CurrentUser(id="dev-user", email="dev@example.com")
        raise HTTPException(401, "Missing bearer token", headers={"WWW-Authenticate": "Bearer"})
    try:
        claims = decode_supabase_token(creds.credentials)
    except AuthError as exc:
        raise HTTPException(401, f"Invalid token: {exc}", headers={"WWW-Authenticate": "Bearer"})
    return CurrentUser(id=claims["sub"], email=claims.get("email"))


DbSession = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]
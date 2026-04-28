from __future__ import annotations

from typing import Annotated, Any

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models.user import User
from .security import decode_access_token
from .settings import settings


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbDep,
    token: Annotated[str | None, Cookie(alias=settings.cookie_name)] = None,
) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload: dict[str, Any] = decode_access_token(token, secret_key=settings.secret_key)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    username = str(payload.get("sub") or "").strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    user = db.query(User).filter(User.username == username).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed_roles: str):
    allowed = set(allowed_roles)

    def _checker(user: CurrentUserDep) -> User:
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return Depends(_checker)


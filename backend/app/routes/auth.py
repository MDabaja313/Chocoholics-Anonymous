from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..deps import CurrentUserDep, DbDep
from ..models.user import User
from ..schemas.auth import LoginRequest, UserMe
from ..security import create_access_token, verify_password
from ..settings import settings


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: DbDep):
    user = db.query(User).filter(User.username == payload.username).one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = create_access_token(
        subject=user.username,
        role=user.role,
        secret_key=settings.secret_key,
        expires_minutes=settings.access_token_expire_minutes,
    )
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return {"result": "OK"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=settings.cookie_name, path="/")
    return {"result": "OK"}


@router.get("/me", response_model=UserMe)
def me(user: CurrentUserDep):
    provider_number = None
    provider_name = None
    if user.provider:
        provider_number = user.provider.provider_number
        provider_name = user.provider.name
    return UserMe(
        username=user.username,
        role=user.role,
        provider_number=provider_number,
        provider_name=provider_name,
    )


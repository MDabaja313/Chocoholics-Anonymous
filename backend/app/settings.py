from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ChocAn DPS"
    secret_key: str = "dev-only-change-me"
    access_token_expire_minutes: int = 60 * 8
    cookie_name: str = "chocan_session"
    cookie_secure: bool = False  # local http
    cookie_samesite: str = "lax"

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()


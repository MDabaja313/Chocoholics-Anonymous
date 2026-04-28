from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class UserMe(BaseModel):
    username: str
    role: str
    provider_number: str | None = None
    provider_name: str | None = None


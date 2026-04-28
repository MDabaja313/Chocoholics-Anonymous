from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from .common import NINE_DIGIT_RE, STATE_RE, ZIP_RE


class MemberBase(BaseModel):
    name: str = Field(min_length=1, max_length=25)
    member_number: str = Field(min_length=9, max_length=9)
    street: str = Field(min_length=1, max_length=25)
    city: str = Field(min_length=1, max_length=14)
    state: str = Field(min_length=2, max_length=2)
    zip_code: str = Field(min_length=5, max_length=5)
    status: str = Field(pattern="^(active|suspended)$")

    @field_validator("member_number")
    @classmethod
    def _member_number_digits(cls, v: str) -> str:
        v = v.strip()
        if not NINE_DIGIT_RE.fullmatch(v):
            raise ValueError("Member number must be exactly 9 digits")
        return v

    @field_validator("state")
    @classmethod
    def _state_two_letters(cls, v: str) -> str:
        v = v.strip().upper()
        if not STATE_RE.fullmatch(v):
            raise ValueError("State must be 2 letters")
        return v

    @field_validator("zip_code")
    @classmethod
    def _zip_five_digits(cls, v: str) -> str:
        v = v.strip()
        if not ZIP_RE.fullmatch(v):
            raise ValueError("ZIP code must be 5 digits")
        return v


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=25)
    street: str | None = Field(default=None, max_length=25)
    city: str | None = Field(default=None, max_length=14)
    state: str | None = Field(default=None, max_length=2)
    zip_code: str | None = Field(default=None, max_length=5)
    status: str | None = Field(default=None, pattern="^(active|suspended)$")

    @field_validator("state")
    @classmethod
    def _state_two_letters(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().upper()
        if not STATE_RE.fullmatch(v):
            raise ValueError("State must be 2 letters")
        return v

    @field_validator("zip_code")
    @classmethod
    def _zip_five_digits(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not ZIP_RE.fullmatch(v):
            raise ValueError("ZIP code must be 5 digits")
        return v


class MemberOut(MemberBase):
    id: int


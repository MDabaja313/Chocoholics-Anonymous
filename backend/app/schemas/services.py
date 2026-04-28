from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from .common import SIX_DIGIT_RE


class ServiceBase(BaseModel):
    code: str = Field(min_length=6, max_length=6)
    name: str = Field(min_length=1, max_length=20)
    fee: Decimal = Field(ge=Decimal("0.00"), le=Decimal("999.99"))

    @field_validator("code")
    @classmethod
    def _code_digits(cls, v: str) -> str:
        v = v.strip()
        if not SIX_DIGIT_RE.fullmatch(v):
            raise ValueError("Service code must be exactly 6 digits")
        return v


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=20)
    fee: Decimal | None = Field(default=None, ge=Decimal("0.00"), le=Decimal("999.99"))


class ServiceOut(ServiceBase):
    id: int


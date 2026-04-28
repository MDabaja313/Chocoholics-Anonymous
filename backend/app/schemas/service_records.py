from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from .common import NINE_DIGIT_RE, SIX_DIGIT_RE, parse_mm_dd_yyyy


class ValidateMemberRequest(BaseModel):
    member_number: str = Field(min_length=9, max_length=9)

    @field_validator("member_number")
    @classmethod
    def _member_number_digits(cls, v: str) -> str:
        v = v.strip()
        if not NINE_DIGIT_RE.fullmatch(v):
            raise ValueError("Member number must be exactly 9 digits")
        return v


class ValidateMemberResponse(BaseModel):
    result: str


class BillServiceRequest(BaseModel):
    date_of_service: str = Field(min_length=10, max_length=10)  # MM-DD-YYYY
    member_number: str = Field(min_length=9, max_length=9)
    service_code: str = Field(min_length=6, max_length=6)
    # Professor requirement: comments are optional, max 100 chars (cap, don't hard-reject).
    comments: str = Field(default="")
    # provider_number optional: providers auto-filled from session; managers/admin can specify
    provider_number: str | None = Field(default=None, min_length=9, max_length=9)

    @field_validator("member_number")
    @classmethod
    def _member_number_digits(cls, v: str) -> str:
        v = v.strip()
        if not NINE_DIGIT_RE.fullmatch(v):
            raise ValueError("Member number must be exactly 9 digits")
        return v

    @field_validator("service_code")
    @classmethod
    def _service_code_digits(cls, v: str) -> str:
        v = v.strip()
        if not SIX_DIGIT_RE.fullmatch(v):
            raise ValueError("Service code must be exactly 6 digits")
        return v

    @field_validator("provider_number")
    @classmethod
    def _provider_number_digits(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not NINE_DIGIT_RE.fullmatch(v):
            raise ValueError("Provider number must be exactly 9 digits")
        return v

    @field_validator("date_of_service")
    @classmethod
    def _dos_format(cls, v: str) -> str:
        _ = parse_mm_dd_yyyy(v.strip())
        return v.strip()

    @field_validator("comments")
    @classmethod
    def _comments_trim(cls, v: str) -> str:
        return (v or "").strip()[:100]


class BillServiceResponse(BaseModel):
    result: str
    fee: Decimal
    service_name: str
    current_date_time: str


class ServiceRecordOut(BaseModel):
    id: int
    current_date_time: str
    date_of_service: str
    provider_number: str
    provider_name: str
    member_number: str
    member_name: str
    service_code: str
    service_name: str
    fee: Decimal
    comments: str


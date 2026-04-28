from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


NINE_DIGIT_RE = re.compile(r"^\d{9}$")
SIX_DIGIT_RE = re.compile(r"^\d{6}$")
STATE_RE = re.compile(r"^[A-Za-z]{2}$")
ZIP_RE = re.compile(r"^\d{5}$")


class Message(BaseModel):
    result: str


def parse_mm_dd_yyyy(value: str) -> date:
    # Accept strict MM-DD-YYYY (as professor spec)
    try:
        mm, dd, yyyy = value.split("-")
        return date(int(yyyy), int(mm), int(dd))
    except Exception as e:
        raise ValueError("Invalid date format (MM-DD-YYYY)") from e


def format_mm_dd_yyyy(d: date) -> str:
    return d.strftime("%m-%d-%Y")


def format_received_ts(dt: datetime) -> str:
    return dt.strftime("%m-%d-%Y %H:%M:%S")


def money(amount: Decimal) -> str:
    return f"${amount:,.2f}"


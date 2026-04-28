from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(25))
    member_number: Mapped[str] = mapped_column(String(9), unique=True, index=True)

    street: Mapped[str] = mapped_column(String(25))
    city: Mapped[str] = mapped_column(String(14))
    state: Mapped[str] = mapped_column(String(2))
    zip_code: Mapped[str] = mapped_column(String(5))

    status: Mapped[str] = mapped_column(String(10), index=True)  # active|suspended


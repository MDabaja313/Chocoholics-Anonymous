from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(25))
    provider_number: Mapped[str] = mapped_column(String(9), unique=True, index=True)

    street: Mapped[str] = mapped_column(String(25))
    city: Mapped[str] = mapped_column(String(14))
    state: Mapped[str] = mapped_column(String(2))
    zip_code: Mapped[str] = mapped_column(String(5))

    status: Mapped[str] = mapped_column(String(10), index=True)  # active|suspended

    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    bank_account: Mapped[str | None] = mapped_column(String(64), nullable=True)

    user = relationship("User", back_populates="provider")


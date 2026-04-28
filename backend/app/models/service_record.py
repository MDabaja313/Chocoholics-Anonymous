from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Professor-required field naming: "current_date_time" (MM-DD-YYYY HH:MM:SS)
    current_date_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    date_of_service: Mapped[date] = mapped_column(Date, index=True)

    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), index=True)

    comments: Mapped[str] = mapped_column(String(100), default="")
    fee_snapshot: Mapped[float] = mapped_column(Numeric(5, 2))

    provider = relationship("Provider")
    member = relationship("Member")
    service = relationship("Service")


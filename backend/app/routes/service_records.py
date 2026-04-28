from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, HTTPException

from ..deps import CurrentUserDep, DbDep, require_roles
from ..models.member import Member
from ..models.provider import Provider
from ..models.service import Service
from ..models.service_record import ServiceRecord
from ..schemas.common import format_mm_dd_yyyy, format_received_ts, parse_mm_dd_yyyy
from ..schemas.service_records import (
    BillServiceRequest,
    BillServiceResponse,
    ServiceRecordOut,
    ValidateMemberRequest,
    ValidateMemberResponse,
)


router = APIRouter(prefix="/api", tags=["provider"])


@router.post("/provider/validate-member", response_model=ValidateMemberResponse, dependencies=[require_roles("provider", "admin")])
def validate_member(payload: ValidateMemberRequest, db: DbDep):
    m = db.query(Member).filter(Member.member_number == payload.member_number).one_or_none()
    if not m:
        return ValidateMemberResponse(result="Invalid number")
    if m.status.lower() == "suspended":
        return ValidateMemberResponse(result="Member suspended")
    return ValidateMemberResponse(result="Validated")


@router.post("/service-records", response_model=BillServiceResponse, dependencies=[require_roles("provider", "manager", "admin")])
def bill_service(payload: BillServiceRequest, db: DbDep, user: CurrentUserDep):
    # Determine provider number: providers must bill as their linked provider.
    provider_number = payload.provider_number
    if user.role == "provider":
        if not user.provider:
            raise HTTPException(status_code=400, detail="Provider user is not linked to a provider record")
        provider_number = user.provider.provider_number
    if not provider_number:
        raise HTTPException(status_code=400, detail="Provider number is required")

    provider = db.query(Provider).filter(Provider.provider_number == provider_number).one_or_none()
    if not provider:
        raise HTTPException(status_code=400, detail="Invalid provider number")
    if provider.status.lower() == "suspended":
        raise HTTPException(status_code=400, detail="Provider suspended")

    member = db.query(Member).filter(Member.member_number == payload.member_number).one_or_none()
    if not member:
        raise HTTPException(status_code=400, detail="Invalid number")
    if member.status.lower() == "suspended":
        raise HTTPException(status_code=400, detail="Member suspended")

    service = db.query(Service).filter(Service.code == payload.service_code).one_or_none()
    if not service:
        raise HTTPException(status_code=400, detail="Invalid service code")

    dos = parse_mm_dd_yyyy(payload.date_of_service)
    current_date_time = datetime.now(UTC).replace(tzinfo=None)  # stored in DB; formatted in responses/reports

    fee = Decimal(str(service.fee))
    record = ServiceRecord(
        current_date_time=current_date_time,
        date_of_service=dos,
        provider_id=provider.id,
        member_id=member.id,
        service_id=service.id,
        comments=(payload.comments or "")[:100],
        fee_snapshot=fee,
    )
    db.add(record)
    db.commit()

    return BillServiceResponse(
        result="Billed",
        fee=fee,
        service_name=service.name,
        current_date_time=format_received_ts(current_date_time),
    )


@router.get("/service-records/mine", response_model=list[ServiceRecordOut], dependencies=[require_roles("provider", "admin")])
def my_service_records(db: DbDep, user: CurrentUserDep):
    if not user.provider:
        raise HTTPException(status_code=400, detail="Provider user is not linked to a provider record")
    provider = user.provider
    records = (
        db.query(ServiceRecord)
        .filter(ServiceRecord.provider_id == provider.id)
        .order_by(ServiceRecord.current_date_time.desc())
        .limit(200)
        .all()
    )
    out: list[ServiceRecordOut] = []
    for r in records:
        out.append(
            ServiceRecordOut(
                id=r.id,
                current_date_time=format_received_ts(r.current_date_time),
                date_of_service=format_mm_dd_yyyy(r.date_of_service),
                provider_number=provider.provider_number,
                provider_name=provider.name,
                member_number=r.member.member_number,
                member_name=r.member.name,
                service_code=r.service.code,
                service_name=r.service.name,
                fee=Decimal(str(r.fee_snapshot)),
                comments=r.comments or "",
            )
        )
    return out


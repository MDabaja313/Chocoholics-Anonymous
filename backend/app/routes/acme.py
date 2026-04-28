from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..deps import DbDep, require_roles
from ..models.member import Member


router = APIRouter(prefix="/api/acme", tags=["acme"])


@router.post("/suspend-member/{member_number}", dependencies=[require_roles("manager", "admin")])
def suspend_member(member_number: str, db: DbDep):
    m = db.query(Member).filter(Member.member_number == member_number.strip()).one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Member not found")
    m.status = "suspended"
    db.commit()
    return {"result": "OK"}


@router.post("/reinstate-member/{member_number}", dependencies=[require_roles("manager", "admin")])
def reinstate_member(member_number: str, db: DbDep):
    m = db.query(Member).filter(Member.member_number == member_number.strip()).one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Member not found")
    m.status = "active"
    db.commit()
    return {"result": "OK"}


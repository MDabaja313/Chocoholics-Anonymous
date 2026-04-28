from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..deps import DbDep, require_roles
from ..models.member import Member
from ..schemas.members import MemberCreate, MemberOut, MemberUpdate


router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("", response_model=list[MemberOut], dependencies=[require_roles("manager", "admin")])
def list_members(db: DbDep, q: str | None = None):
    query = db.query(Member)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter((Member.name.ilike(like)) | (Member.member_number.ilike(like)))
    return query.order_by(Member.name.asc()).all()


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED, dependencies=[require_roles("manager", "admin")])
def create_member(payload: MemberCreate, db: DbDep):
    exists = db.query(Member).filter(Member.member_number == payload.member_number).one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Member number already exists")
    m = Member(**payload.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/{member_number}", response_model=MemberOut, dependencies=[require_roles("manager", "admin")])
def update_member(member_number: str, payload: MemberUpdate, db: DbDep):
    m = db.query(Member).filter(Member.member_number == member_number.strip()).one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Member not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return m


@router.delete("/{member_number}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[require_roles("manager", "admin")])
def delete_member(member_number: str, db: DbDep):
    m = db.query(Member).filter(Member.member_number == member_number.strip()).one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(m)
    db.commit()
    return None


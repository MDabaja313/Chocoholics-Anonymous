from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..deps import DbDep, require_roles
from ..models.service import Service
from ..schemas.services import ServiceCreate, ServiceOut, ServiceUpdate


router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=list[ServiceOut], dependencies=[require_roles("provider", "manager", "admin")])
def list_services(db: DbDep, q: str | None = None):
    query = db.query(Service)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter((Service.name.ilike(like)) | (Service.code.ilike(like)))
    return query.order_by(Service.name.asc()).all()


@router.get("/by-code/{code}", response_model=ServiceOut, dependencies=[require_roles("provider", "manager", "admin")])
def get_service_by_code(code: str, db: DbDep):
    s = db.query(Service).filter(Service.code == code.strip()).one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Service code not found")
    return s


@router.post("", response_model=ServiceOut, status_code=status.HTTP_201_CREATED, dependencies=[require_roles("manager", "admin")])
def create_service(payload: ServiceCreate, db: DbDep):
    exists = db.query(Service).filter(Service.code == payload.code).one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Service code already exists")
    s = Service(**payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.put("/{code}", response_model=ServiceOut, dependencies=[require_roles("manager", "admin")])
def update_service(code: str, payload: ServiceUpdate, db: DbDep):
    s = db.query(Service).filter(Service.code == code.strip()).one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[require_roles("manager", "admin")])
def delete_service(code: str, db: DbDep):
    s = db.query(Service).filter(Service.code == code.strip()).one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(s)
    db.commit()
    return None


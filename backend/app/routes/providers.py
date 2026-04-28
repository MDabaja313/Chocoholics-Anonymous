from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..deps import DbDep, require_roles
from ..models.provider import Provider
from ..schemas.providers import ProviderCreate, ProviderOut, ProviderUpdate


router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("", response_model=list[ProviderOut], dependencies=[require_roles("manager", "admin")])
def list_providers(db: DbDep, q: str | None = None):
    query = db.query(Provider)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter((Provider.name.ilike(like)) | (Provider.provider_number.ilike(like)))
    return query.order_by(Provider.name.asc()).all()


@router.post("", response_model=ProviderOut, status_code=status.HTTP_201_CREATED, dependencies=[require_roles("manager", "admin")])
def create_provider(payload: ProviderCreate, db: DbDep):
    exists = db.query(Provider).filter(Provider.provider_number == payload.provider_number).one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Provider number already exists")
    p = Provider(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{provider_number}", response_model=ProviderOut, dependencies=[require_roles("manager", "admin")])
def update_provider(provider_number: str, payload: ProviderUpdate, db: DbDep):
    p = db.query(Provider).filter(Provider.provider_number == provider_number.strip()).one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{provider_number}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[require_roles("manager", "admin")])
def delete_provider(provider_number: str, db: DbDep):
    p = db.query(Provider).filter(Provider.provider_number == provider_number.strip()).one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")
    db.delete(p)
    db.commit()
    return None


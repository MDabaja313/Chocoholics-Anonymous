from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import APIRouter

from ..deps import DbDep, require_roles
from ..models.service import Service


router = APIRouter(prefix="/api/directory", tags=["directory"])

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = REPO_ROOT / "generated_reports"


@router.get("", dependencies=[require_roles("provider", "manager", "admin")])
def get_directory(db: DbDep):
    services = db.query(Service).order_by(Service.name.asc()).all()
    return {
        "services": [
            {"name": s.name, "code": s.code, "fee": float(s.fee)}
            for s in services
        ]
    }


@router.post("/generate", dependencies=[require_roles("provider", "manager", "admin")])
def generate_directory_file(db: DbDep):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    services = db.query(Service).order_by(Service.name.asc()).all()

    lines: list[str] = []
    lines.append("ChocAn Provider Directory")
    lines.append(f"Date: {date.today().isoformat()}")
    lines.append("")
    lines.append("Service Name | Service Code | Fee")
    lines.append("-" * 60)
    for s in services:
        lines.append(f"{s.name} | {s.code} | ${float(s.fee):.2f}")

    filename = f"Provider_Directory_{date.today().isoformat()}.txt"
    path = REPORTS_DIR / filename
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"result": "OK", "filename": filename}


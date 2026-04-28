from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..deps import DbDep, require_roles
from ..services.reporting import generate_weekly_reports


router = APIRouter(prefix="/api/reports", tags=["reports"])


REPO_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = REPO_ROOT / "generated_reports"


@router.post("/run-weekly", dependencies=[require_roles("manager", "admin")])
def run_weekly_reports(db: DbDep):
    generated = generate_weekly_reports(db=db, reports_dir=REPORTS_DIR, today=date.today())
    return {
        "result": "OK",
        "generated": {
            "member_reports": [p.name for p in generated.member_reports],
            "provider_reports": [p.name for p in generated.provider_reports],
            "summary_report": generated.summary_report.name,
            "eft_file": generated.eft_file.name,
        },
    }


@router.get("/files", dependencies=[require_roles("manager", "admin")])
def list_report_files():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted([p.name for p in REPORTS_DIR.iterdir() if p.is_file() and p.suffix.lower() == ".txt"])
    return {"files": files}


@router.get("/files/{filename}", dependencies=[require_roles("manager", "admin")])
def download_report_file(filename: str):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name
    path = REPORTS_DIR / safe_name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="text/plain", filename=safe_name)


import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from modules.validation import get_member, get_provider, get_service, validate_member, validate_provider


def _read_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _write_json_list(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def bill_service(
    *,
    provider_number: str,
    member_number: str,
    service_code: str,
    date_of_service: str,
    comments: Optional[str],
    data_dir: Path,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    prov_status = validate_provider(provider_number, data_dir)
    if prov_status != "Validated":
        return False, prov_status, None

    mem_status = validate_member(member_number, data_dir)
    if mem_status != "Validated":
        return False, mem_status, None

    service = get_service(service_code, data_dir)
    if not service:
        return False, "Invalid service code", None

    provider = get_provider(provider_number, data_dir)
    member = get_member(member_number, data_dir)
    if not provider or not member:
        return False, "Invalid number", None

    record: Dict[str, Any] = {
        "current_date_time": datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
        "provider_number": provider_number,
        "provider_name": str(provider.get("name", "")).strip(),
        "member_number": member_number,
        "member_name": str(member.get("name", "")).strip(),
        "service_code": str(service.get("code", "")).strip(),
        "service_name": str(service.get("name", "")).strip(),
        "fee": float(service.get("fee", 0) or 0),
        "date_of_service": str(date_of_service).strip(),
        "comments": (comments or "").strip()[:100],
    }

    log_path = data_dir / "services_log.json"
    log = _read_json_list(log_path)
    log.append(record)
    _write_json_list(log_path, log)
    return True, "Billed", record

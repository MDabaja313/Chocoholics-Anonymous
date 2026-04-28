import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _read_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _find_by_key(records: List[Dict[str, Any]], key: str, value: str) -> Optional[Dict[str, Any]]:
    for r in records:
        if str(r.get(key, "")).strip() == str(value).strip():
            return r
    return None


def validate_member(member_number: str, data_dir: Path) -> str:
    members = _read_json_list(data_dir / "members.json")
    member = _find_by_key(members, "member_number", member_number)
    if not member:
        return "Invalid number"
    status = str(member.get("status", "active")).lower().strip()
    if status == "suspended":
        return "Member suspended"
    return "Validated"


def validate_provider(provider_number: str, data_dir: Path) -> str:
    providers = _read_json_list(data_dir / "providers.json")
    provider = _find_by_key(providers, "provider_number", provider_number)
    if not provider:
        return "Invalid number"
    status = str(provider.get("status", "active")).lower().strip()
    if status == "suspended":
        return "Provider suspended"
    return "Validated"


def get_member(member_number: str, data_dir: Path) -> Optional[Dict[str, Any]]:
    members = _read_json_list(data_dir / "members.json")
    return _find_by_key(members, "member_number", member_number)


def get_provider(provider_number: str, data_dir: Path) -> Optional[Dict[str, Any]]:
    providers = _read_json_list(data_dir / "providers.json")
    return _find_by_key(providers, "provider_number", provider_number)


def get_service(service_code: str, data_dir: Path) -> Optional[Dict[str, Any]]:
    services = _read_json_list(data_dir / "services.json")
    return _find_by_key(services, "code", service_code)


def provider_directory(data_dir: Path) -> List[Dict[str, Any]]:
    services = _read_json_list(data_dir / "services.json")
    cleaned: List[Dict[str, Any]] = []
    for s in services:
        cleaned.append(
            {
                "name": str(s.get("name", "")).strip(),
                "code": str(s.get("code", "")).strip(),
                "fee": float(s.get("fee", 0) or 0),
            }
        )
    cleaned.sort(key=lambda x: x["name"].lower())
    return cleaned

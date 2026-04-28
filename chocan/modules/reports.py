import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _read_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _safe_filename(name: str) -> str:
    name = name.strip() or "unknown"
    name = re.sub(r"[^\w\- ]+", "", name)
    name = re.sub(r"\s+", "_", name).strip("_")
    return name[:80] if len(name) > 80 else name


def _money(amount: float) -> str:
    return f"${amount:,.2f}"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _today_str() -> str:
    return date.today().strftime("%m-%d-%Y")


def generate_reports(*, data_dir: Path, outputs_dir: Path) -> Dict[str, List[str]]:
    logs = _read_json_list(data_dir / "services_log.json")
    members = {str(m.get("member_number", "")).strip(): m for m in _read_json_list(data_dir / "members.json")}
    providers = {str(p.get("provider_number", "")).strip(): p for p in _read_json_list(data_dir / "providers.json")}
    today = _today_str()

    member_groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    provider_groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}

    total_fees = 0.0
    total_consultations = 0
    for r in logs:
        mem_key = (str(r.get("member_number", "")).strip(), str(r.get("member_name", "")).strip())
        prov_key = (str(r.get("provider_number", "")).strip(), str(r.get("provider_name", "")).strip())
        member_groups.setdefault(mem_key, []).append(r)
        provider_groups.setdefault(prov_key, []).append(r)
        total_consultations += 1
        try:
            total_fees += float(r.get("fee", 0) or 0)
        except Exception:
            pass

    generated_members: List[str] = []
    for (mem_no, mem_name), records in sorted(member_groups.items(), key=lambda x: x[0][1].lower()):
        records_sorted = sorted(records, key=lambda x: (str(x.get("date_of_service", "")), str(x.get("provider_name", "")).lower()))
        m = members.get(mem_no, {})
        lines: List[str] = []
        lines.append("ChocAn Data Processing System")
        lines.append("Member Report")
        lines.append(f"Date: {today}")
        lines.append("")
        lines.append(f"Member Name: {mem_name}")
        lines.append(f"Member Number: {mem_no}")
        lines.append(f"Street Address: {m.get('street_address', 'N/A')}")
        lines.append(f"City: {m.get('city', 'N/A')}")
        lines.append(f"State: {m.get('state', 'N/A')}")
        lines.append(f"ZIP: {m.get('zip_code', 'N/A')}")
        lines.append("")
        lines.append("Services Received:")
        if not records_sorted:
            lines.append("  (none)")
        else:
            for r in records_sorted:
                lines.append(f"- Date of Service: {r.get('date_of_service','')}")
                lines.append(f"  Provider: {r.get('provider_name','')} ({r.get('provider_number','')})")
                lines.append(f"  Service: {r.get('service_name','')} ({r.get('service_code','')})")
                lines.append("")

        filename = f"{_safe_filename(mem_name)}_{today}.txt"
        out_path = outputs_dir / filename
        _write_text(out_path, "\n".join(lines).rstrip() + "\n")
        generated_members.append(str(out_path))

    generated_providers: List[str] = []
    provider_totals: Dict[Tuple[str, str], float] = {}
    for (prov_no, prov_name), records in sorted(provider_groups.items(), key=lambda x: x[0][1].lower()):
        records_sorted = sorted(records, key=lambda x: (str(x.get("date_of_service", "")), str(x.get("member_name", "")).lower()))
        p = providers.get(prov_no, {})
        lines: List[str] = []
        lines.append("ChocAn Data Processing System")
        lines.append("Provider Report")
        lines.append(f"Date: {today}")
        lines.append("")
        lines.append(f"Provider Name: {prov_name}")
        lines.append(f"Provider Number: {prov_no}")
        lines.append(f"Street Address: {p.get('street_address', 'N/A')}")
        lines.append(f"City: {p.get('city', 'N/A')}")
        lines.append(f"State: {p.get('state', 'N/A')}")
        lines.append(f"ZIP: {p.get('zip_code', 'N/A')}")
        lines.append("")
        lines.append("Services Provided:")

        provider_fee_total = 0.0
        if not records_sorted:
            lines.append("  (none)")
        else:
            for r in records_sorted:
                fee = float(r.get("fee", 0) or 0)
                provider_fee_total += fee
                lines.append(f"- Date of Service: {r.get('date_of_service','')}")
                lines.append(f"  Date/Time Received: {r.get('date_time_received','')}")
                lines.append(f"  Member: {r.get('member_name','')} ({r.get('member_number','')})")
                lines.append(f"  Service Code: {r.get('service_code','')}")
                lines.append(f"  Fee: {_money(fee)}")
                lines.append("")

        lines.append(f"Total Consultations: {len(records_sorted)}")
        lines.append(f"Total Fees: {_money(provider_fee_total)}")
        provider_totals[(prov_no, prov_name)] = provider_fee_total

        filename = f"{_safe_filename(prov_name)}_{today}.txt"
        out_path = outputs_dir / filename
        _write_text(out_path, "\n".join(lines).rstrip() + "\n")
        generated_providers.append(str(out_path))

    summary_lines: List[str] = []
    summary_lines.append("ChocAn Data Processing System")
    summary_lines.append("Manager Summary Report")
    summary_lines.append(f"Date: {today}")
    summary_lines.append("")
    summary_lines.append("Provider Totals:")
    if not provider_totals:
        summary_lines.append("  (none)")
    else:
        for (prov_no, prov_name), amt in sorted(provider_totals.items(), key=lambda x: x[0][1].lower()):
            consults = len(provider_groups[(prov_no, prov_name)])
            summary_lines.append(f"- {prov_name} ({prov_no}): {consults} consultations, {_money(amt)}")
    summary_lines.append("")
    summary_lines.append(f"Total Providers: {len(provider_totals)}")
    summary_lines.append(f"Total Consultations: {total_consultations}")
    summary_lines.append(f"Total Fees: {_money(total_fees)}")
    summary_path = outputs_dir / f"SummaryReport_{today}.txt"
    _write_text(summary_path, "\n".join(summary_lines).rstrip() + "\n")

    eft_lines: List[str] = []
    eft_lines.append("ChocAn EFT File")
    eft_lines.append(f"Date: {today}")
    eft_lines.append("")
    for (prov_no, prov_name), amt in sorted(provider_totals.items(), key=lambda x: x[0][1].lower()):
        eft_lines.append(f"{prov_name} | {prov_no} | {_money(amt)}")
    eft_path = outputs_dir / f"EFT_{today}.txt"
    _write_text(eft_path, "\n".join(eft_lines).rstrip() + "\n")

    return {
        "member_reports": generated_members,
        "provider_reports": generated_providers,
        "summary_report": [str(summary_path)],
        "eft_file": [str(eft_path)],
    }


def generate_provider_directory(*, data_dir: Path, outputs_dir: Path) -> str:
    logs = _read_json_list(data_dir / "services_log.json")
    seen = {}
    for r in logs:
        code = str(r.get("service_code", "")).strip()
        name = str(r.get("service_name", "")).strip()
        fee = float(r.get("fee", 0) or 0)
        if code and name and code not in seen:
            seen[code] = (name, fee)
    lines: List[str] = []
    lines.append("ChocAn Provider Directory")
    lines.append(f"Date: {_today_str()}")
    lines.append("")
    for name, fee in sorted(seen.values(), key=lambda x: x[0].lower()):
        code = [k for k, v in seen.items() if v[0] == name][0]
        lines.append(f"{name} | Code: {code} | Fee: {_money(fee)}")
    out_path = outputs_dir / "ProviderDirectory.txt"
    _write_text(out_path, "\n".join(lines).rstrip() + "\n")
    return str(out_path)
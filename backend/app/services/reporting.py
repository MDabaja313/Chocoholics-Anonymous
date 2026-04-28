from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from ..models.member import Member
from ..models.provider import Provider
from ..models.service_record import ServiceRecord
from ..schemas.common import format_mm_dd_yyyy, format_received_ts, money


def _safe_filename(name: str) -> str:
    name = (name or "").strip() or "unknown"
    name = re.sub(r"[^\w\- ]+", "", name)
    name = re.sub(r"\s+", "_", name).strip("_")
    return name[:80] if len(name) > 80 else name


def calendar_week_bounds(today: date) -> tuple[date, date]:
    # Monday..Sunday inclusive
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


@dataclass(frozen=True)
class GeneratedReportPaths:
    member_reports: list[Path]
    provider_reports: list[Path]
    summary_report: Path
    eft_file: Path


def generate_weekly_reports(*, db: Session, reports_dir: Path, today: date) -> GeneratedReportPaths:
    reports_dir.mkdir(parents=True, exist_ok=True)

    week_start, week_end = calendar_week_bounds(today)

    # Filter by date_of_service within week
    records: list[ServiceRecord] = (
        db.query(ServiceRecord)
        .filter(ServiceRecord.date_of_service >= week_start)
        .filter(ServiceRecord.date_of_service <= week_end)
        .order_by(ServiceRecord.date_of_service.asc())
        .all()
    )

    # Group by member/provider
    member_groups: dict[int, list[ServiceRecord]] = {}
    provider_groups: dict[int, list[ServiceRecord]] = {}
    for r in records:
        member_groups.setdefault(r.member_id, []).append(r)
        provider_groups.setdefault(r.provider_id, []).append(r)

    # Member reports
    member_paths: list[Path] = []
    for member_id, recs in sorted(member_groups.items(), key=lambda kv: kv[0]):
        m: Member = recs[0].member
        recs_sorted = sorted(recs, key=lambda r: (r.date_of_service, r.provider.name.lower()))

        lines: list[str] = []
        lines.append("ChocAn Data Processing System")
        lines.append("Member Report")
        lines.append(f"Week: {week_start.isoformat()} to {week_end.isoformat()}")
        lines.append(f"Report Date: {today.isoformat()}")
        lines.append("")
        lines.append(f"Member Name: {m.name}")
        lines.append(f"Member Number: {m.member_number}")
        lines.append(f"Member Street Address: {m.street}")
        lines.append(f"Member City: {m.city}")
        lines.append(f"Member State: {m.state}")
        lines.append(f"Member ZIP Code: {m.zip_code}")
        lines.append("")
        lines.append("Services Received:")
        if not recs_sorted:
            lines.append("  (none)")
        else:
            for r in recs_sorted:
                lines.append(f"- Date of Service: {format_mm_dd_yyyy(r.date_of_service)}")
                lines.append(f"  Provider Name: {r.provider.name}")
                lines.append(f"  Service Name: {r.service.name}")
                lines.append("")

        filename = f"{_safe_filename(m.name)}_{today.isoformat()}.txt"
        path = reports_dir / filename
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        member_paths.append(path)

    # Provider reports + totals
    provider_paths: list[Path] = []
    provider_totals: dict[int, Decimal] = {}
    provider_consults: dict[int, int] = {}

    for provider_id, recs in sorted(provider_groups.items(), key=lambda kv: kv[0]):
        p: Provider = recs[0].provider
        recs_sorted = sorted(recs, key=lambda r: (r.date_of_service, r.current_date_time))

        total_fee = Decimal("0.00")
        lines: list[str] = []
        lines.append("ChocAn Data Processing System")
        lines.append("Provider Report")
        lines.append(f"Week: {week_start.isoformat()} to {week_end.isoformat()}")
        lines.append(f"Report Date: {today.isoformat()}")
        lines.append("")
        lines.append(f"Provider Name: {p.name}")
        lines.append(f"Provider Number: {p.provider_number}")
        lines.append(f"Provider Street Address: {p.street}")
        lines.append(f"Provider City: {p.city}")
        lines.append(f"Provider State: {p.state}")
        lines.append(f"Provider ZIP Code: {p.zip_code}")
        lines.append("")
        lines.append("Services Provided:")

        for r in recs_sorted:
            fee = Decimal(str(r.fee_snapshot))
            total_fee += fee
            lines.append(f"- Date of Service: {format_mm_dd_yyyy(r.date_of_service)}")
            lines.append(f"  Date and Time Data Were Received by Computer: {format_received_ts(r.current_date_time)}")
            lines.append(f"  Member Name: {r.member.name}")
            lines.append(f"  Member Number: {r.member.member_number}")
            lines.append(f"  Service Code: {r.service.code}")
            lines.append(f"  Fee: {money(fee)}")
            lines.append("")

        lines.append(f"Total Number of Consultations: {len(recs_sorted)}")
        lines.append(f"Total Fee for Week: {money(total_fee)}")

        provider_totals[provider_id] = total_fee
        provider_consults[provider_id] = len(recs_sorted)

        filename = f"{_safe_filename(p.name)}_{today.isoformat()}.txt"
        path = reports_dir / filename
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        provider_paths.append(path)

    # Manager summary
    summary_lines: list[str] = []
    summary_lines.append("ChocAn Data Processing System")
    summary_lines.append("Manager Summary Report")
    summary_lines.append(f"Week: {week_start.isoformat()} to {week_end.isoformat()}")
    summary_lines.append(f"Report Date: {today.isoformat()}")
    summary_lines.append("")
    summary_lines.append("Providers to be paid:")

    overall_fees = Decimal("0.00")
    overall_consults = 0
    for provider_id, amt in sorted(provider_totals.items(), key=lambda kv: kv[0]):
        p = db.query(Provider).filter(Provider.id == provider_id).one()
        consults = provider_consults.get(provider_id, 0)
        summary_lines.append(f"- Provider: {p.name} ({p.provider_number})")
        summary_lines.append(f"  Consultations: {consults}")
        summary_lines.append(f"  Total Fee: {money(amt)}")
        overall_fees += amt
        overall_consults += consults

    summary_lines.append("")
    summary_lines.append(f"Total Providers with Consultations: {len(provider_totals)}")
    summary_lines.append(f"Total Consultations: {overall_consults}")
    summary_lines.append(f"Overall Fee Total: {money(overall_fees)}")

    summary_path = reports_dir / f"Summary_{today.isoformat()}.txt"
    summary_path.write_text("\n".join(summary_lines).rstrip() + "\n", encoding="utf-8")

    # EFT file
    eft_lines: list[str] = []
    eft_lines.append("ChocAn EFT File")
    eft_lines.append(f"Week: {week_start.isoformat()} to {week_end.isoformat()}")
    eft_lines.append(f"Report Date: {today.isoformat()}")
    eft_lines.append("")
    eft_lines.append("provider_number,provider_name,amount")
    for provider_id, amt in sorted(provider_totals.items(), key=lambda kv: kv[0]):
        p = db.query(Provider).filter(Provider.id == provider_id).one()
        eft_lines.append(f"{p.provider_number},{p.name},{amt:.2f}")

    eft_path = reports_dir / f"EFT_{today.isoformat()}.txt"
    eft_path.write_text("\n".join(eft_lines).rstrip() + "\n", encoding="utf-8")

    return GeneratedReportPaths(
        member_reports=member_paths,
        provider_reports=provider_paths,
        summary_report=summary_path,
        eft_file=eft_path,
    )


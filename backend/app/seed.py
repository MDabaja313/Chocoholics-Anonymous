from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from .database import SessionLocal, engine, init_db
from .database import Base
from .models.member import Member
from .models.provider import Provider
from .models.service import Service
from .models.service_record import ServiceRecord
from .models.user import User
from .security import hash_password


def reset_db() -> None:
    # On Windows, deleting the SQLite file can fail if another process
    # temporarily holds a handle. Dropping/recreating tables is reliable.
    init_db()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed(db: Session) -> None:
    # Providers
    providers = [
        Provider(
            name="Nora Patel",
            provider_number="200000001",
            street="12 Clinic Rd",
            city="Portland",
            state="OR",
            zip_code="97201",
            status="active",
            email="npatel@example.com",
            bank_account="EFT-0001",
        ),
        Provider(
            name="Evergreen Wellness",
            provider_number="200000002",
            street="55 Pine St",
            city="Salem",
            state="OR",
            zip_code="97301",
            status="active",
            email="billing@evergreen.example.com",
            bank_account="EFT-0002",
        ),
        Provider(
            name="Sunrise Counseling",
            provider_number="200000003",
            street="88 Sunrise Ave",
            city="Eugene",
            state="OR",
            zip_code="97401",
            status="suspended",
            email=None,
            bank_account="EFT-0003",
        ),
    ]
    db.add_all(providers)

    # Members
    members = [
        Member(
            name="Alice Rivera",
            member_number="100000001",
            street="101 Main St",
            city="Portland",
            state="OR",
            zip_code="97201",
            status="active",
        ),
        Member(
            name="Brandon Lee",
            member_number="100000002",
            street="202 Oak St",
            city="Salem",
            state="OR",
            zip_code="97301",
            status="suspended",
        ),
        Member(
            name="Carmen Diaz",
            member_number="100000003",
            street="303 Cedar St",
            city="Eugene",
            state="OR",
            zip_code="97401",
            status="active",
        ),
        Member(
            name="Devon Kim",
            member_number="100000004",
            street="404 Maple St",
            city="Bend",
            state="OR",
            zip_code="97701",
            status="active",
        ),
        Member(
            name="Evelyn Chen",
            member_number="100000005",
            street="505 Birch St",
            city="Corvallis",
            state="OR",
            zip_code="97330",
            status="active",
        ),
    ]
    db.add_all(members)

    # Services (must include professor examples)
    services = [
        Service(code="598470", name="Dietitian Session", fee=Decimal("50.00")),
        Service(code="883948", name="Aerobics Session", fee=Decimal("60.00")),
        Service(code="112233", name="Nutrition Coaching", fee=Decimal("45.00")),
        Service(code="445566", name="Group Support", fee=Decimal("35.00")),
        Service(code="778899", name="Relapse Workshop", fee=Decimal("75.00")),
        Service(code="123456", name="Stress Management", fee=Decimal("55.00")),
        Service(code="654321", name="Behavior Therapy", fee=Decimal("80.00")),
        Service(code="111222", name="Health Screening", fee=Decimal("40.00")),
    ]
    db.add_all(services)

    db.flush()

    # Users
    provider1 = providers[0]
    users = [
        User(username="admin", password_hash=hash_password("admin123"), role="admin", provider_id=None),
        User(username="manager", password_hash=hash_password("manager123"), role="manager", provider_id=None),
        User(username="provider1", password_hash=hash_password("provider123"), role="provider", provider_id=provider1.id),
    ]
    db.add_all(users)
    db.flush()

    # Sample service records inside current calendar week (Mon-Sun).
    # We'll add a couple dated "this week" relative to today.
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    sample_date = week_start
    r1 = ServiceRecord(
        current_date_time=datetime.now(),
        date_of_service=sample_date,
        provider_id=providers[0].id,
        member_id=members[0].id,
        service_id=services[0].id,
        comments="seed record",
        fee_snapshot=services[0].fee,
    )
    r2 = ServiceRecord(
        current_date_time=datetime.now(),
        date_of_service=sample_date + timedelta(days=1),
        provider_id=providers[1].id,
        member_id=members[2].id,
        service_id=services[1].id,
        comments="seed record 2",
        fee_snapshot=services[1].fee,
    )
    db.add_all([r1, r2])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Delete and recreate the SQLite database.")
    args = parser.parse_args()

    if args.reset:
        reset_db()

    init_db()
    db = SessionLocal()
    try:
        seed(db)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()


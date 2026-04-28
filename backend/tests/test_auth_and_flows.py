from __future__ import annotations

from fastapi.testclient import TestClient


def login_as(client: TestClient, username: str, password: str) -> None:
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text


def test_login_roles_me(client: TestClient):
    login_as(client, "provider1", "provider123")
    me = client.get("/api/auth/me").json()
    assert me["role"] == "provider"
    assert me["provider_number"] == "200000001"

    client.post("/api/auth/logout")

    login_as(client, "manager", "manager123")
    me = client.get("/api/auth/me").json()
    assert me["role"] == "manager"

    client.post("/api/auth/logout")

    login_as(client, "admin", "admin123")
    me = client.get("/api/auth/me").json()
    assert me["role"] == "admin"


def test_member_validation_active_suspended_invalid(client: TestClient):
    login_as(client, "provider1", "provider123")

    r = client.post("/api/provider/validate-member", json={"member_number": "100000001"}).json()
    assert r["result"] == "Validated"

    r = client.post("/api/provider/validate-member", json={"member_number": "100000002"}).json()
    assert r["result"] == "Member suspended"

    r = client.post("/api/provider/validate-member", json={"member_number": "999999999"}).json()
    assert r["result"] == "Invalid number"


def test_billing_valid_creates_record_and_caps_comments(client: TestClient):
    login_as(client, "provider1", "provider123")

    long_comment = "x" * 200
    res = client.post(
        "/api/service-records",
        json={
            "date_of_service": "04-28-2026",
            "member_number": "100000001",
            "service_code": "598470",
            "comments": long_comment,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["result"] == "Billed"
    assert "current_date_time" in body

    mine = client.get("/api/service-records/mine")
    assert mine.status_code == 200
    records = mine.json()
    assert len(records) >= 1
    assert len(records[0]["comments"]) <= 100


def test_billing_invalid_service_code_does_not_create_record(client: TestClient):
    login_as(client, "provider1", "provider123")
    before = client.get("/api/service-records/mine").json()

    res = client.post(
        "/api/service-records",
        json={
            "date_of_service": "04-28-2026",
            "member_number": "100000001",
            "service_code": "000000",
            "comments": "",
        },
    )
    assert res.status_code == 400

    after = client.get("/api/service-records/mine").json()
    assert len(after) == len(before)


def test_provider_directory_from_services_even_without_billing(client: TestClient):
    login_as(client, "provider1", "provider123")
    directory = client.get("/api/directory").json()
    services = directory["services"]
    assert len(services) >= 5
    names = [s["name"] for s in services]
    assert names == sorted(names, key=lambda x: x.lower())


def test_reports_generate_and_include_files(client: TestClient):
    login_as(client, "manager", "manager123")
    run = client.post("/api/reports/run-weekly")
    assert run.status_code == 200
    files = client.get("/api/reports/files").json()["files"]
    assert any(f.startswith("Summary_") for f in files)
    assert any(f.startswith("EFT_") for f in files)


def test_acme_suspend_and_reinstate_reflects_in_members(client: TestClient):
    login_as(client, "manager", "manager123")
    members = client.get("/api/members").json()
    target = next(m for m in members if m["member_number"] == "100000001")
    assert target["status"] == "active"

    res = client.post("/api/acme/suspend-member/100000001")
    assert res.status_code == 200
    members = client.get("/api/members").json()
    target = next(m for m in members if m["member_number"] == "100000001")
    assert target["status"] == "suspended"

    res = client.post("/api/acme/reinstate-member/100000001")
    assert res.status_code == 200
    members = client.get("/api/members").json()
    target = next(m for m in members if m["member_number"] == "100000001")
    assert target["status"] == "active"


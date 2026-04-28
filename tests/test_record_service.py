import json
import re
import sys
from pathlib import Path

import pytest


# Allow "import app" from the chocan/ folder.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "chocan"))

from app import create_app  # noqa: E402


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


@pytest.fixture()
def env(tmp_path: Path):
    data_dir = tmp_path / "data"
    outputs_dir = tmp_path / "outputs"

    write_json(
        data_dir / "members.json",
        [
            {"member_number": "100000001", "name": "Alice Rivera", "status": "active"},
        ],
    )
    write_json(
        data_dir / "providers.json",
        [
            {"provider_number": "200000001", "name": "Dr. Nora Patel", "status": "active"},
        ],
    )
    write_json(
        data_dir / "services.json",
        [
            {"code": "598470", "name": "Chocolate Addiction Counseling", "fee": 125.0},
        ],
    )
    write_json(data_dir / "services_log.json", [])

    app = create_app(data_dir=data_dir, outputs_dir=outputs_dir)
    app.config.update(TESTING=True)
    client = app.test_client()
    return {"client": client, "data_dir": data_dir}


def load_log(data_dir: Path) -> list[dict]:
    with (data_dir / "services_log.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def post_bill(client, **overrides):
    payload = {
        "provider_number": "200000001",
        "member_number": "100000001",
        "service_code": "598470",
        "date_of_service": "04-28-2026",
        "comments": "ok",
    }
    payload.update(overrides)
    return client.post("/bill_service", json=payload)


def test_1_valid_inputs_service_recorded_fee_returned(env):
    client = env["client"]
    data_dir = env["data_dir"]

    res = post_bill(client, comments="test charge")
    assert res.status_code == 200
    body = res.get_json()
    assert body["result"] == "Billed"
    assert body["record"]["fee"] == 125.0

    log = load_log(data_dir)
    assert len(log) == 1
    assert log[0]["fee"] == 125.0


def test_2_bad_service_code_error_no_record_written(env):
    client = env["client"]
    data_dir = env["data_dir"]

    res = post_bill(client, service_code="000000")
    assert res.status_code == 400
    log = load_log(data_dir)
    assert len(log) == 0


def test_3_blank_comments_record_saved_successfully(env):
    client = env["client"]
    data_dir = env["data_dir"]

    res = post_bill(client, comments="")
    assert res.status_code == 200
    body = res.get_json()
    assert body["record"]["comments"] == ""

    log = load_log(data_dir)
    assert len(log) == 1
    assert log[0]["comments"] == ""


def test_4_wrong_date_format_rejected(env):
    client = env["client"]
    data_dir = env["data_dir"]

    res = post_bill(client, date_of_service="2026/04/28")
    assert res.status_code == 400
    log = load_log(data_dir)
    assert len(log) == 0


def test_5_verify_all_fields_present_in_saved_record(env):
    client = env["client"]
    data_dir = env["data_dir"]

    res = post_bill(client, comments="hello")
    assert res.status_code == 200
    log = load_log(data_dir)
    assert len(log) == 1
    r = log[0]

    for k in [
        "current_date_time",
        "date_of_service",
        "provider_number",
        "member_number",
        "service_code",
        "comments",
    ]:
        assert k in r

    assert re.fullmatch(r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}", r["current_date_time"])

from __future__ import annotations

from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.database import Base, SessionLocal, engine  # noqa: E402
from backend.app.main import create_app  # noqa: E402
from backend.app.seed import seed  # noqa: E402


@pytest.fixture()
def client(tmp_path: Path):
    # Use the existing engine but reset tables for each test run.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed(db)
        db.commit()
    finally:
        db.close()

    app = create_app()
    with TestClient(app) as c:
        yield c


def login_as(client: TestClient, username: str, password: str) -> None:
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text


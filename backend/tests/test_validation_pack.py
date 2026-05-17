import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app import models  # noqa: E402,F401
from app.database import Base, get_db
from app.main import app
from app.models import BusinessScenario
from app.seed import seed_tenayan
from app.services import shortlist
from app.services.port_intelligence import normalize_wpi_port


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def deterministic_ports(monkeypatch: pytest.MonkeyPatch) -> None:
    port = normalize_wpi_port(
        {
            "portNumber": 1,
            "portName": "Committee Port",
            "countryCode": "ID",
            "countryName": "Indonesia",
            "xcoord": 101.6,
            "ycoord": 0.55,
            "harborSize": "L",
            "harborType": "CN",
            "chDepth": "14",
            "anDepth": "12",
            "loWharves": "Y",
            "loContainer": "Y",
            "loLiquidBulk": "Y",
            "firstPortOfEntry": "Y",
            "tugsAssist": "Y",
            "cmRadio": "Y",
            "turningArea": "Y",
            "etaMessage": "Y",
        }
    )
    assert port is not None
    monkeypatch.setattr(shortlist, "load_wpi_ports", lambda _: (port,))


def _seed_outputs(client: TestClient, db_session: Session) -> str:
    plant = seed_tenayan(db_session)
    scenario = db_session.scalar(select(BusinessScenario).where(BusinessScenario.plant_id == plant.id))
    assert scenario is not None
    assert client.post(f"/api/scenarios/{scenario.id}/simulate").status_code == 200
    assert client.post("/api/scoring/recalculate", json={"scenario_id": scenario.id}).status_code == 200
    return plant.id


def test_top3_validation_pack_returns_candidate_and_memo(
    client: TestClient,
    db_session: Session,
) -> None:
    plant_id = _seed_outputs(client, db_session)

    response = client.get("/api/validation-pack/top3?scheme=align")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["candidate_count"] == 1
    assert payload["summary"]["lead_candidate"] == "PLTU Tenayan"
    assert payload["summary"]["high_priority_evidence_count"] >= 1
    candidate = payload["candidates"][0]
    assert candidate["plant_id"] == plant_id
    assert candidate["nearest_port_name"] == "Committee Port"
    assert candidate["validation_items"]
    assert any(item["category"] == "Economics" for item in candidate["validation_items"])
    assert payload["committee_memo"]["decision_questions"]
    assert payload["comparison_axes"]


def test_committee_memo_pdf_endpoint_returns_pdf(
    client: TestClient,
    db_session: Session,
) -> None:
    _seed_outputs(client, db_session)

    response = client.get("/api/validation-pack/committee-memo.pdf?scheme=align")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 1000

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
            "portName": "Decision Port",
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


def _seed_outputs(client: TestClient, db_session: Session) -> tuple[str, str]:
    plant = seed_tenayan(db_session)
    scenario = db_session.scalar(select(BusinessScenario).where(BusinessScenario.plant_id == plant.id))
    assert scenario is not None
    assert client.post(f"/api/scenarios/{scenario.id}/simulate").status_code == 200
    assert client.post("/api/scoring/recalculate", json={"scenario_id": scenario.id}).status_code == 200
    return plant.id, scenario.id


def test_pilot_decision_defaults_to_continue_validation(
    client: TestClient,
    db_session: Session,
) -> None:
    plant_id, scenario_id = _seed_outputs(client, db_session)

    response = client.get("/api/pilot-decision?scheme=align")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["recommended_candidate"] == "PLTU Tenayan"
    assert payload["summary"]["committee_ready_count"] == 0
    assert payload["summary"]["high_priority_open_items"] == 4
    candidate = payload["candidates"][0]
    assert candidate["plant_id"] == plant_id
    assert candidate["scenario_id"] == scenario_id
    assert candidate["gate_status"] == "needs_evidence"
    assert candidate["recommendation"] == "continue_validation"
    assert candidate["blockers"]
    assert payload["action_plan"]


def test_pilot_decision_advances_when_all_evidence_is_verified(
    client: TestClient,
    db_session: Session,
) -> None:
    _seed_outputs(client, db_session)
    workspace = client.get("/api/evidence/workspace?scheme=align").json()
    for item in workspace["candidates"][0]["evidence_items"]:
        response = client.post(
            "/api/evidence/records",
            json={
                "plant_id": item["plant_id"],
                "scenario_id": item["scenario_id"],
                "category": item["category"],
                "evidence_key": item["evidence_key"],
                "title": item["title"],
                "required_evidence": item["required_evidence"],
                "current_basis": item["current_basis"],
                "status": "verified",
                "priority": item["priority"],
                "confidence_level": "high",
            },
        )
        assert response.status_code == 201

    response = client.get("/api/pilot-decision?scheme=align")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["committee_ready_count"] == 1
    assert payload["summary"]["high_priority_open_items"] == 0
    candidate = payload["candidates"][0]
    assert candidate["gate_status"] == "committee_ready"
    assert candidate["recommendation"] == "advance_to_committee"
    assert candidate["evidence_readiness_score"] == 100
    assert candidate["verified_items"] == 5

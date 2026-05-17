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
from app.models import BusinessScenario, ValidationEvidence
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
            "portName": "Evidence Port",
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


def test_evidence_workspace_returns_default_top3_requirements(
    client: TestClient,
    db_session: Session,
) -> None:
    plant_id, scenario_id = _seed_outputs(client, db_session)

    response = client.get("/api/evidence/workspace?scheme=align")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["candidate_count"] == 1
    assert payload["summary"]["total_items"] == 5
    assert payload["summary"]["verified_items"] == 0
    assert payload["summary"]["counts_by_status"]["missing"] == 5
    candidate = payload["candidates"][0]
    assert candidate["plant_id"] == plant_id
    assert candidate["scenario_id"] == scenario_id
    assert candidate["evidence_readiness_score"] == 0
    assert {item["category"] for item in candidate["evidence_items"]} == {
        "technical",
        "economics",
        "logistics",
        "power_h2",
        "commercial_mrv",
    }


def test_create_evidence_record_updates_workspace_rollup(
    client: TestClient,
    db_session: Session,
) -> None:
    plant_id, scenario_id = _seed_outputs(client, db_session)

    create_response = client.post(
        "/api/evidence/records",
        json={
            "plant_id": plant_id,
            "scenario_id": scenario_id,
            "category": "logistics",
            "evidence_key": "port_export_route",
            "title": "Port and export handling route",
            "required_evidence": "Terminal confirmation and route cost.",
            "current_basis": "Evidence Port straight-line proxy",
            "status": "verified",
            "priority": "high",
            "owner_name": "PLN site team",
            "source_organization": "Terminal operator",
            "confidence_level": "high",
            "notes": "Route desk validation completed.",
        },
    )

    assert create_response.status_code == 201
    record = create_response.json()
    assert record["status"] == "verified"
    assert record["received_date"] is not None
    assert record["verified_date"] is not None

    workspace = client.get("/api/evidence/workspace?scheme=align").json()
    assert workspace["summary"]["verified_items"] == 1
    assert workspace["summary"]["counts_by_status"]["verified"] == 1
    assert workspace["summary"]["evidence_readiness_score"] > 0
    logistics = [
        item
        for item in workspace["candidates"][0]["evidence_items"]
        if item["evidence_key"] == "port_export_route"
    ][0]
    assert logistics["status"] == "verified"
    assert logistics["record"]["owner_name"] == "PLN site team"


def test_update_evidence_record_changes_status(
    client: TestClient,
    db_session: Session,
) -> None:
    plant_id, scenario_id = _seed_outputs(client, db_session)
    created = client.post(
        "/api/evidence/records",
        json={
            "plant_id": plant_id,
            "scenario_id": scenario_id,
            "category": "technical",
            "evidence_key": "site_stack_profile",
            "title": "Site, unit, capacity, stack, and operating profile",
            "status": "requested",
            "priority": "high",
            "confidence_level": "unknown",
        },
    ).json()

    response = client.put(
        f"/api/evidence/records/{created['id']}",
        json={
            "status": "received",
            "confidence_level": "medium",
            "notes": "CEMS export received, pending technical verification.",
        },
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "received"
    assert updated["confidence_level"] == "medium"
    assert updated["received_date"] is not None
    persisted = db_session.get(ValidationEvidence, created["id"])
    assert persisted is not None
    assert persisted.status == "received"

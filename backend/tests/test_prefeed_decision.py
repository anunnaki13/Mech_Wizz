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
from app.models import BusinessScenario, PreFeedPackage, ScenarioResult
from app.seed import seed_tenayan


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


def _seed_package(db: Session) -> tuple[PreFeedPackage, BusinessScenario]:
    plant = seed_tenayan(db)
    scenario = db.scalar(select(BusinessScenario).where(BusinessScenario.plant_id == plant.id))
    assert scenario is not None
    package = PreFeedPackage(
        plant_id=plant.id,
        scenario_id=scenario.id,
        package_name="Tenayan Decision Package",
        package_status="in_review",
        version_label="rev-decision",
        data_status="partner_supplied",
        confidence_level="medium",
    )
    result = ScenarioResult(
        scenario_id=scenario.id,
        total_co2_ton_per_year=1_000_000,
        captured_co2_ton_per_year=850_000,
        vented_co2_ton_per_year=150_000,
        methanol_ton_per_year=500_000,
        h2_required_ton_per_year=93_750,
        electrolyzer_required_mw=600,
        gross_revenue_usd_per_year=450_000_000,
        lcom_usd_per_ton=None,
        npv_usd=None,
        irr=None,
        payback_years=None,
        missing_inputs=[],
        assumption_snapshot={},
        calculation_version="test",
        confidence_level="medium",
    )
    db.add_all([package, result])
    db.commit()
    db.refresh(package)
    return package, scenario


def test_risk_register_summary_blockers_and_dashboard_are_deterministic(
    client: TestClient,
    db_session: Session,
) -> None:
    package, scenario = _seed_package(db_session)
    before_results = len(list(db_session.scalars(select(ScenarioResult))))

    risk_response = client.post(
        f"/api/prefeed/packages/{package.id}/risks",
        json={
            "category": "grid",
            "risk_statement": "Grid interconnection schedule could slip beyond committee target.",
            "likelihood": 4,
            "impact": 5,
            "mitigation": "Escalate grid study and assign PLN owner.",
            "owner_name": "Grid Lead",
            "due_date": "2026-06-30",
            "status": "escalated",
            "data_status": "partner_supplied",
            "confidence_level": "medium",
        },
    )
    assert risk_response.status_code == 201
    risk = risk_response.json()
    assert risk["severity_score"] == 20
    assert risk["severity_band"] == "critical"

    summary_response = client.get(f"/api/prefeed/packages/{package.id}/risk-summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["risk_count"] == 1
    assert summary["escalated_risk_count"] == 1
    assert summary["severity_distribution"]["critical"] == 1
    assert summary["top_risks"][0]["id"] == risk["id"]

    gate_response = client.post(
        f"/api/prefeed/packages/{package.id}/decision-gates",
        json={
            "category": "mrv",
            "gate_title": "MRV methodology selected",
            "evidence_reference": "Methodology note pending third-party review.",
            "owner_name": "MRV Lead",
            "due_date": "2026-06-15",
            "is_critical": True,
            "status": "blocked",
            "data_status": "estimated",
            "confidence_level": "low",
        },
    )
    assert gate_response.status_code == 201
    gate = gate_response.json()
    assert gate["is_critical"] is True

    gate_summary_response = client.get(f"/api/prefeed/packages/{package.id}/decision-gate-summary")
    assert gate_summary_response.status_code == 200
    gate_summary = gate_summary_response.json()
    assert gate_summary["gate_count"] == 1
    assert gate_summary["blocked_gate_count"] == 1
    assert gate_summary["critical_blocker_count"] == 1
    assert gate_summary["readiness_score"] == 0

    blockers_response = client.get(f"/api/prefeed/packages/{package.id}/decision-blockers")
    assert blockers_response.status_code == 200
    blocker_titles = {blocker["title"] for blocker in blockers_response.json()}
    assert "Grid interconnection schedule could slip beyond committee target." in blocker_titles
    assert "MRV methodology selected" in blocker_titles

    next_actions_response = client.get(f"/api/prefeed/packages/{package.id}/decision-next-actions")
    assert next_actions_response.status_code == 200
    assert next_actions_response.json()[0]["priority_level"] == "critical"

    dashboard_response = client.get(f"/api/prefeed/packages/{package.id}/decision-dashboard")
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["package_id"] == package.id
    assert dashboard["scenario_id"] == scenario.id
    assert dashboard["risk_summary"]["severity_distribution"]["critical"] == 1
    assert dashboard["decision_gate_summary"]["critical_blocker_count"] == 1
    assert dashboard["blockers"]
    assert "No active cost basis selected" in " ".join(dashboard["warnings"])
    assert len(list(db_session.scalars(select(ScenarioResult)))) == before_results

    update_response = client.put(f"/api/prefeed/risks/{risk['id']}", json={"status": "mitigating", "likelihood": 3})
    assert update_response.status_code == 200
    assert update_response.json()["severity_score"] == 15

    delete_gate_response = client.delete(f"/api/prefeed/decision-gates/{gate['id']}")
    assert delete_gate_response.status_code == 204

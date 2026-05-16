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
from app.models import (
    BusinessScenario,
    Document,
    FinancialAssumption,
    PreFeedCostBasisSelection,
    PreFeedPackage,
    ScenarioResult,
)
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
        package_name="Tenayan Cost Package",
        package_status="in_review",
        version_label="rev-cost",
        data_status="partner_supplied",
        confidence_level="medium",
    )
    db.add(package)
    db.commit()
    db.refresh(package)
    return package, scenario


def _create_document(db: Session, package: PreFeedPackage, scenario_id: str) -> Document:
    document = Document(
        plant_id=package.plant_id,
        scenario_id=scenario_id,
        filename="vendor-proposal.txt",
        original_filename="vendor-proposal.txt",
        file_type="text/plain",
        storage_path="/tmp/vendor-proposal.txt",
        document_category="vendor_proposal",
        upload_status="uploaded",
        extraction_status="pending",
        file_size_bytes=256,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def test_cost_item_crud_and_summary_do_not_mutate_financial_assumptions(
    client: TestClient,
    db_session: Session,
) -> None:
    package, scenario = _seed_package(db_session)
    capex_response = client.post(
        f"/api/prefeed/packages/{package.id}/cost-items",
        json={
            "cost_type": "capex",
            "cost_component": "capture_package",
            "amount": 100.0,
            "currency": "usd",
            "contingency_percent": 10,
            "escalation_percent": 5,
            "source_label": "EPC estimate",
            "data_status": "partner_supplied",
            "confidence_level": "medium",
        },
    )
    assert capex_response.status_code == 201
    capex_item = capex_response.json()
    assert capex_item["currency"] == "USD"

    opex_response = client.post(
        f"/api/prefeed/packages/{package.id}/cost-items",
        json={
            "cost_type": "opex",
            "cost_component": "fixed_opex",
            "amount": 10.0,
            "currency": "USD",
            "unit_basis": "month",
            "recurrence": "monthly",
            "source_label": "O&M estimate",
            "data_status": "estimated",
            "confidence_level": "low",
        },
    )
    assert opex_response.status_code == 201

    list_response = client.get(f"/api/prefeed/packages/{package.id}/cost-items")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    summary_response = client.get(f"/api/prefeed/packages/{package.id}/cost-summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["capex_total_by_currency"]["USD"] == 115.5
    assert summary["annual_opex_total_by_currency"]["USD"] == 120.0
    assert summary["scenario_ready_assumptions"]["capex_capture_usd"] == 115.5

    assumption = db_session.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id))
    assert assumption is not None
    assert assumption.capex_capture_usd is None

    update_response = client.put(f"/api/prefeed/cost-items/{capex_item['id']}", json={"amount": 120.0})
    assert update_response.status_code == 200
    assert update_response.json()["amount"] == 120.0

    delete_response = client.delete(f"/api/prefeed/cost-items/{capex_item['id']}")
    assert delete_response.status_code == 204


def test_vendor_proposal_comparison_gaps_and_active_selection_preserve_history(
    client: TestClient,
    db_session: Session,
) -> None:
    package, scenario = _seed_package(db_session)
    document = _create_document(db_session, package, scenario.id)
    proposal_response = client.post(
        f"/api/prefeed/packages/{package.id}/vendor-proposals",
        json={
            "supporting_document_id": document.id,
            "vendor_name": "EPC Alpha",
            "proposal_name": "Alpha Rev A",
            "scope_capture_package": True,
            "scope_electrolyzer": True,
            "scope_methanol_plant": True,
            "scope_storage_port": False,
            "scope_grid_power": False,
            "scope_land": False,
            "scope_mrv": False,
            "commercial_basis": "Lump sum EPC estimate",
            "validity_date": "2026-12-31",
            "data_status": "partner_supplied",
            "confidence_level": "medium",
        },
    )
    assert proposal_response.status_code == 201
    proposal = proposal_response.json()
    assert proposal["supporting_document"]["original_filename"] == "vendor-proposal.txt"

    cost_response = client.post(
        f"/api/prefeed/packages/{package.id}/cost-items",
        json={
            "vendor_proposal_id": proposal["id"],
            "cost_type": "capex",
            "cost_component": "electrolyzer",
            "amount": 250.0,
            "currency": "USD",
            "confidence_level": "medium",
        },
    )
    assert cost_response.status_code == 201

    comparison_response = client.get(f"/api/prefeed/packages/{package.id}/vendor-comparison")
    assert comparison_response.status_code == 200
    comparison = comparison_response.json()
    assert len(comparison) == 1
    assert comparison[0]["vendor_name"] == "EPC Alpha"
    assert comparison[0]["capex_total_by_currency"]["USD"] == 250.0
    assert "storage_port" in comparison[0]["missing_scopes"]
    assert comparison[0]["scope_completeness_score"] < 1

    gaps_response = client.get(f"/api/prefeed/vendor-proposals/{proposal['id']}/gaps")
    assert gaps_response.status_code == 200
    gap_names = {gap["missing_data_name"] for gap in gaps_response.json()}
    assert "Storage Port scope" in gap_names
    assert "Grid Power scope" in gap_names

    before_results = len(list(db_session.scalars(select(ScenarioResult))))
    active_response = client.post(
        f"/api/prefeed/scenarios/{scenario.id}/active-cost-basis",
        json={
            "package_id": package.id,
            "vendor_proposal_id": proposal["id"],
            "selection_type": "vendor_proposal",
            "selected_by": "Pre-FEED team",
            "selection_notes": "Use Alpha as current basis",
        },
    )
    assert active_response.status_code == 200
    active = active_response.json()
    assert active["is_active"] is True
    assert active["vendor_proposal_id"] == proposal["id"]
    assert active["scenario_ready_assumptions"]["capex_electrolyzer_usd"] == 250.0
    assert len(list(db_session.scalars(select(ScenarioResult)))) == before_results

    second_response = client.post(
        f"/api/prefeed/scenarios/{scenario.id}/active-cost-basis",
        json={
            "package_id": package.id,
            "selection_type": "blended_package",
            "selected_by": "Pre-FEED team",
        },
    )
    assert second_response.status_code == 200
    selections = list(
        db_session.scalars(
            select(PreFeedCostBasisSelection).where(PreFeedCostBasisSelection.scenario_id == scenario.id)
        )
    )
    assert len(selections) == 2
    assert sum(1 for selection in selections if selection.is_active) == 1

    read_active_response = client.get(f"/api/prefeed/scenarios/{scenario.id}/active-cost-basis")
    assert read_active_response.status_code == 200
    assert read_active_response.json()["selection_type"] == "blended_package"

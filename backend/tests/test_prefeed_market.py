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
    PreFeedPackage,
    PreFeedPriceDeck,
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
        package_name="Tenayan Market Package",
        package_status="in_review",
        version_label="rev-market",
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


def _create_document(db: Session, package: PreFeedPackage, scenario_id: str, category: str) -> Document:
    document = Document(
        plant_id=package.plant_id,
        scenario_id=scenario_id,
        filename=f"{category}.txt",
        original_filename=f"{category}.txt",
        file_type="text/plain",
        storage_path=f"/tmp/{category}.txt",
        document_category=category,
        upload_status="uploaded",
        extraction_status="completed",
        file_size_bytes=256,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def test_offtake_price_decks_summary_gaps_and_history_are_deterministic(
    client: TestClient,
    db_session: Session,
) -> None:
    package, scenario = _seed_package(db_session)
    document = _create_document(db_session, package, scenario.id, "offtake_document")

    first_deck = client.post(
        f"/api/prefeed/packages/{package.id}/price-decks",
        json={
            "deck_name": "Base Market Deck",
            "is_active": True,
            "methanol_price_usd_per_ton": 900,
            "carbon_credit_price_usd_per_ton": 8,
            "electricity_price_usd_per_kwh": 0.06,
            "hydrogen_price_usd_per_kg": 3,
            "exchange_rate_idr_usd": 17000,
            "data_status": "benchmark",
            "confidence_level": "medium",
        },
    )
    assert first_deck.status_code == 201
    second_deck = client.post(
        f"/api/prefeed/packages/{package.id}/price-decks",
        json={
            "deck_name": "Partner Deck",
            "is_active": True,
            "methanol_price_usd_per_ton": 1000,
            "carbon_credit_price_usd_per_ton": 10,
            "electricity_price_usd_per_kwh": 0.05,
            "hydrogen_price_usd_per_kg": 2.8,
            "exchange_rate_idr_usd": 17500,
            "data_status": "partner_supplied",
            "confidence_level": "high",
        },
    )
    assert second_deck.status_code == 201
    decks = list(db_session.scalars(select(PreFeedPriceDeck).where(PreFeedPriceDeck.package_id == package.id)))
    assert len(decks) == 2
    assert sum(1 for deck in decks if deck.is_active) == 1
    assert next(deck for deck in decks if deck.is_active).deck_name == "Partner Deck"

    prospect_response = client.post(
        f"/api/prefeed/packages/{package.id}/offtake-prospects",
        json={
            "supporting_document_id": document.id,
            "counterparty_name": "Green Methanol Buyer",
            "product": "e_methanol",
            "target_volume_tpy": 250000,
            "term_years": 8,
            "pricing_basis": "Fixed annual floor price",
            "status": "term_sheet",
            "data_status": "partner_supplied",
            "confidence_level": "medium",
        },
    )
    assert prospect_response.status_code == 201

    before_assumption = db_session.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id))
    assert before_assumption is not None
    assert before_assumption.methanol_price_usd_per_ton == 1250

    summary_response = client.get(f"/api/prefeed/packages/{package.id}/offtake-summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["active_price_deck_id"] == second_deck.json()["id"]
    assert summary["methanol_volume_committed_tpy"] == 250000
    assert summary["methanol_volume_coverage"] == 0.5
    assert summary["methanol_revenue_usd_per_year"] == 250_000_000
    assert summary["carbon_credit_revenue_usd_per_year"] == 8_500_000
    assert summary["gross_revenue_usd_per_year"] == 258_500_000
    assert summary["scenario_ready_assumptions"]["methanol_price_usd_per_ton"] == 1000
    assert summary["scenario_ready_assumptions"]["carbon_credit_price_idr_per_ton"] == 175000
    assert summary["readiness_score"] > 0.5

    after_assumption = db_session.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id))
    assert after_assumption is not None
    assert after_assumption.methanol_price_usd_per_ton == 1250

    gaps_response = client.get(f"/api/prefeed/packages/{package.id}/offtake-gaps")
    assert gaps_response.status_code == 200
    gap_names = {gap["missing_data_name"] for gap in gaps_response.json()}
    assert "Active price deck" not in gap_names
    assert all(gap["owner"] == "Commercial" for gap in gaps_response.json())

    inactive_response = client.put(f"/api/prefeed/offtake-prospects/{prospect_response.json()['id']}", json={"status": "inactive"})
    assert inactive_response.status_code == 200
    delete_response = client.delete(f"/api/prefeed/price-decks/{first_deck.json()['id']}")
    assert delete_response.status_code == 204


def test_mrv_assumptions_summary_gaps_and_credit_eligibility(
    client: TestClient,
    db_session: Session,
) -> None:
    package, scenario = _seed_package(db_session)
    document = _create_document(db_session, package, scenario.id, "mrv_document")

    mrv_response = client.post(
        f"/api/prefeed/packages/{package.id}/mrv-assumptions",
        json={
            "supporting_document_id": document.id,
            "baseline_emissions_tco2e_per_year": 1000000,
            "captured_co2_accounting_tpy": 850000,
            "product_carbon_intensity_tco2e_per_ton": 0.3,
            "electricity_source": "Grid plus REC screening",
            "electricity_emission_factor_tco2e_per_mwh": 0.2,
            "methanol_pathway": "Captured CO2 to e-methanol",
            "carbon_credit_methodology": "Voluntary carbon screening",
            "verification_status": "third_party_review",
            "verifier_name": "Verifier Alpha",
            "carbon_credit_eligibility": "potentially_eligible",
            "eligibility_basis": "Methodology screening note",
            "data_status": "partner_supplied",
            "confidence_level": "medium",
        },
    )
    assert mrv_response.status_code == 201
    assumption = mrv_response.json()
    assert assumption["supporting_document"]["original_filename"] == "mrv_document.txt"

    summary_response = client.get(f"/api/prefeed/packages/{package.id}/mrv-summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["assumption_id"] == assumption["id"]
    assert summary["carbon_intensity_tco2e_per_ton_methanol"] == 0.3
    assert summary["abatement_tco2e_per_year"] == 850000
    assert summary["carbon_credit_eligibility"] == "potentially_eligible"
    assert summary["readiness_score"] > 0.6

    gaps_response = client.get(f"/api/prefeed/packages/{package.id}/mrv-gaps")
    assert gaps_response.status_code == 200
    assert gaps_response.json() == []

    update_response = client.put(
        f"/api/prefeed/mrv-assumptions/{assumption['id']}",
        json={"verification_status": "verified", "carbon_credit_eligibility": "eligible"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["verification_status"] == "verified"

    delete_response = client.delete(f"/api/prefeed/mrv-assumptions/{assumption['id']}")
    assert delete_response.status_code == 204
    empty_gaps = client.get(f"/api/prefeed/packages/{package.id}/mrv-gaps")
    assert empty_gaps.status_code == 200
    assert empty_gaps.json()[0]["missing_data_name"] == "MRV assumptions"

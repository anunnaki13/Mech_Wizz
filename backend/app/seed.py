from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.database import SessionLocal
from app.models import BusinessScenario, EmissionTest, FinancialAssumption, Plant


TENAYAN_PLANT = {
    "plant_name": "PLTU Tenayan",
    "unit_name": "Unit 1-2",
    "province": "Riau",
    "city": "Pekanbaru",
    "capacity_mw": 220,
    "fuel_type": "coal",
    "status": "active",
    "capacity_factor": 0.90,
    "operating_days_per_year": 330,
    "owner": "PLN NP",
    "data_status": "actual",
    "confidence_level": "medium",
}

TENAYAN_EMISSION_TESTS = [
    {
        "stack_id": "Chimney #1",
        "stack_diameter_m": 3.0,
        "gas_velocity_m_s": 14.4,
        "flue_gas_temperature_c": 124,
        "co2_percent_dry": 8.48,
        "o2_percent": 9.54,
        "moisture_percent": 5.84,
        "so2_mg_nm3": 233,
        "nox_mg_nm3": 263,
        "particulate_mg_nm3": 55.4,
        "data_status": "actual",
        "confidence_level": "medium",
    },
    {
        "stack_id": "Chimney #2",
        "stack_diameter_m": 3.0,
        "gas_velocity_m_s": 13.5,
        "flue_gas_temperature_c": 109,
        "co2_percent_dry": 3.54,
        "o2_percent": 15.0,
        "moisture_percent": 6.48,
        "so2_mg_nm3": 268,
        "nox_mg_nm3": 202,
        "particulate_mg_nm3": 52.3,
        "data_status": "actual",
        "confidence_level": "medium",
    },
]

TENAYAN_SCENARIO = {
    "scenario_name": "WIZ Align Base Case",
    "scheme": "align",
    "pln_ownership_percent": 25,
    "partner_capex_responsibility_percent": 100,
    "pln_capex_responsibility_percent": 0,
    "revenue_model": "equity_share_plus_asset_revenue",
    "capture_rate": 0.85,
    "process_efficiency": 0.60,
    "data_status": "user_assumption",
    "confidence_level": "medium",
}

TENAYAN_FINANCIAL_ASSUMPTIONS = {
    "methanol_price_usd_per_ton": 1250,
    "grey_methanol_price_usd_per_ton": 350,
    "hydrogen_price_usd_per_kg": 3.0,
    "electricity_price_usd_per_kwh": 0.06,
    "carbon_credit_price_idr_per_ton": 58800,
    "exchange_rate_idr_usd": 17500,
    "discount_rate": 0.10,
    "tax_rate": 0.22,
    "capex_capture_usd": None,
    "capex_electrolyzer_usd": None,
    "capex_methanol_plant_usd": None,
    "capex_storage_port_usd": None,
    "opex_percent_capex": 0.04,
    "data_status": "benchmark",
    "confidence_level": "low",
}


def seed_tenayan(db: Session) -> Plant:
    plant = db.scalar(
        select(Plant).where(
            Plant.plant_name == TENAYAN_PLANT["plant_name"],
            Plant.unit_name == TENAYAN_PLANT["unit_name"],
        )
    )
    if plant is None:
        plant = Plant(**TENAYAN_PLANT)
        db.add(plant)
    else:
        for field, value in TENAYAN_PLANT.items():
            setattr(plant, field, value)

    db.commit()
    db.refresh(plant)
    seed_tenayan_emission_tests(db, plant)
    seed_tenayan_scenario(db, plant)
    return plant


def seed_tenayan_emission_tests(db: Session, plant: Plant) -> list[EmissionTest]:
    records: list[EmissionTest] = []
    for row in TENAYAN_EMISSION_TESTS:
        emission_test = db.scalar(
            select(EmissionTest).where(
                EmissionTest.plant_id == plant.id,
                EmissionTest.stack_id == row["stack_id"],
            )
        )
        if emission_test is None:
            emission_test = EmissionTest(plant_id=plant.id, **row)
            db.add(emission_test)
        else:
            for field, value in row.items():
                setattr(emission_test, field, value)
        records.append(emission_test)

    db.commit()
    for record in records:
        db.refresh(record)
    return records


def seed_tenayan_scenario(db: Session, plant: Plant) -> BusinessScenario:
    scenario = db.scalar(
        select(BusinessScenario).where(
            BusinessScenario.plant_id == plant.id,
            BusinessScenario.scenario_name == TENAYAN_SCENARIO["scenario_name"],
        )
    )
    if scenario is None:
        scenario = BusinessScenario(plant_id=plant.id, **TENAYAN_SCENARIO)
        db.add(scenario)
    else:
        for field, value in TENAYAN_SCENARIO.items():
            setattr(scenario, field, value)

    db.commit()
    db.refresh(scenario)
    seed_tenayan_financial_assumptions(db, scenario)
    return scenario


def seed_tenayan_financial_assumptions(db: Session, scenario: BusinessScenario) -> FinancialAssumption:
    record = db.scalar(
        select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id)
    )
    if record is None:
        record = FinancialAssumption(scenario_id=scenario.id, **TENAYAN_FINANCIAL_ASSUMPTIONS)
        db.add(record)
    else:
        for field, value in TENAYAN_FINANCIAL_ASSUMPTIONS.items():
            setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


def main() -> None:
    with SessionLocal() as db:
        plant = seed_tenayan(db)
        print(f"Seeded {plant.plant_name} {plant.unit_name}")


if __name__ == "__main__":
    main()

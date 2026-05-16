from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BusinessScenario, EmissionTest, FinancialAssumption, Plant, ScenarioResult
from app.services.calculations.co2 import calculate_total_co2_ton_year
from app.services.calculations.defaults import DEFAULT_PROCESS_EFFICIENCY, DEFAULT_PROJECT_LIFE_YEARS
from app.services.calculations.financial import (
    calculate_annual_cashflow_usd,
    calculate_annual_opex_usd,
    calculate_annualized_capex_usd,
    calculate_carbon_credit_price_usd_per_ton,
    calculate_electricity_cost_usd_per_year,
    calculate_gross_revenue_usd_per_year,
    calculate_h2_cost_usd_per_year,
    calculate_lcom_usd_per_ton,
    calculate_npv,
    calculate_payback_years,
    calculate_project_irr,
    calculate_total_capex_usd,
)
from app.services.calculations.hydrogen import calculate_electrolyzer_mw, calculate_h2_required_ton_year
from app.services.calculations.methanol import (
    calculate_captured_co2_ton_year,
    calculate_methanol_actual_ton_year,
    calculate_methanol_theoretical_ton_year,
    calculate_vented_co2_ton_year,
)


CALCULATION_VERSION = "phase2-v1"
DEFAULT_CAPTURE_RATE = 0.85


class SimulationInputError(ValueError):
    pass


def _snapshot_fields(record: object | None, fields: list[str]) -> dict[str, Any] | None:
    if record is None:
        return None
    return {field: getattr(record, field) for field in fields}


def _append_missing_for_none(missing_inputs: list[str], prefix: str, record: object, fields: list[str]) -> None:
    for field in fields:
        if getattr(record, field) is None:
            missing_inputs.append(f"{prefix}.{field}")


def _result_confidence(
    scenario: BusinessScenario,
    financial_assumption: FinancialAssumption | None,
    missing_inputs: list[str],
    financial_outputs: list[float | None],
) -> str:
    if missing_inputs or any(value is None for value in financial_outputs):
        return "low"
    if financial_assumption and (
        financial_assumption.confidence_level == "low" or financial_assumption.data_status == "benchmark"
    ):
        return "low"
    return scenario.confidence_level


def run_scenario_simulation(db: Session, scenario_id: str) -> ScenarioResult:
    scenario = db.get(BusinessScenario, scenario_id)
    if scenario is None:
        raise SimulationInputError("Scenario not found")

    plant = db.get(Plant, scenario.plant_id)
    if plant is None:
        raise SimulationInputError("Plant not found")

    emission_tests = list(db.scalars(select(EmissionTest).where(EmissionTest.plant_id == plant.id)))
    financial_assumption = db.scalar(
        select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id)
    )

    missing_inputs: list[str] = []
    if not emission_tests:
        missing_inputs.append("emission_tests")
    if plant.operating_days_per_year is None:
        missing_inputs.append("plants.operating_days_per_year")

    capture_rate = scenario.capture_rate if scenario.capture_rate is not None else DEFAULT_CAPTURE_RATE
    process_efficiency = (
        scenario.process_efficiency if scenario.process_efficiency is not None else DEFAULT_PROCESS_EFFICIENCY
    )
    if scenario.capture_rate is None:
        missing_inputs.append("business_scenarios.capture_rate")
    if scenario.process_efficiency is None:
        missing_inputs.append("business_scenarios.process_efficiency")

    total_co2 = calculate_total_co2_ton_year(emission_tests, plant.operating_days_per_year)
    if total_co2 is None:
        missing_inputs.append("emission_tests.complete_stack_data")

    captured_co2 = calculate_captured_co2_ton_year(total_co2, capture_rate)
    vented_co2 = calculate_vented_co2_ton_year(total_co2, captured_co2)
    methanol_theoretical = calculate_methanol_theoretical_ton_year(captured_co2)
    methanol_actual = calculate_methanol_actual_ton_year(methanol_theoretical, process_efficiency)
    h2_required = calculate_h2_required_ton_year(methanol_actual)
    electrolyzer_mw = calculate_electrolyzer_mw(h2_required, plant.operating_days_per_year)

    gross_revenue = None
    lcom = None
    npv = None
    irr = None
    payback = None

    if financial_assumption is None:
        missing_inputs.append("financial_assumptions")
    else:
        _append_missing_for_none(
            missing_inputs,
            "financial_assumptions",
            financial_assumption,
            [
                "methanol_price_usd_per_ton",
                "carbon_credit_price_idr_per_ton",
                "exchange_rate_idr_usd",
                "hydrogen_price_usd_per_kg",
                "electricity_price_usd_per_kwh",
                "discount_rate",
                "tax_rate",
                "capex_capture_usd",
                "capex_electrolyzer_usd",
                "capex_methanol_plant_usd",
                "capex_storage_port_usd",
                "opex_percent_capex",
            ],
        )

        carbon_price_usd = calculate_carbon_credit_price_usd_per_ton(
            financial_assumption.carbon_credit_price_idr_per_ton,
            financial_assumption.exchange_rate_idr_usd,
        )
        gross_revenue = calculate_gross_revenue_usd_per_year(
            methanol_actual,
            financial_assumption.methanol_price_usd_per_ton,
            captured_co2,
            carbon_price_usd,
        )
        total_capex = calculate_total_capex_usd(
            financial_assumption.capex_capture_usd,
            financial_assumption.capex_electrolyzer_usd,
            financial_assumption.capex_methanol_plant_usd,
            financial_assumption.capex_storage_port_usd,
        )
        annualized_capex = calculate_annualized_capex_usd(
            total_capex,
            financial_assumption.discount_rate,
            DEFAULT_PROJECT_LIFE_YEARS,
        )
        annual_opex = calculate_annual_opex_usd(total_capex, financial_assumption.opex_percent_capex)
        annual_h2_cost = calculate_h2_cost_usd_per_year(
            h2_required,
            financial_assumption.hydrogen_price_usd_per_kg,
        )
        annual_electricity_cost = calculate_electricity_cost_usd_per_year(
            electrolyzer_mw,
            plant.operating_days_per_year,
            financial_assumption.electricity_price_usd_per_kwh,
        )
        lcom = calculate_lcom_usd_per_ton(
            methanol_actual,
            annualized_capex,
            annual_opex,
            annual_h2_cost,
            annual_electricity_cost,
        )
        annual_cashflow = calculate_annual_cashflow_usd(
            gross_revenue,
            annual_opex,
            annual_h2_cost,
            annual_electricity_cost,
            financial_assumption.tax_rate,
        )
        npv = calculate_npv(
            total_capex,
            annual_cashflow,
            financial_assumption.discount_rate,
            DEFAULT_PROJECT_LIFE_YEARS,
        )
        irr = calculate_project_irr(total_capex, annual_cashflow, DEFAULT_PROJECT_LIFE_YEARS)
        payback = calculate_payback_years(total_capex, annual_cashflow)
        if annual_cashflow is not None and annual_cashflow <= 0:
            missing_inputs.append("financial_cashflow.non_positive")

    financial_outputs = [gross_revenue, lcom, npv, irr, payback]
    confidence = _result_confidence(scenario, financial_assumption, missing_inputs, financial_outputs)

    result = ScenarioResult(
        scenario_id=scenario.id,
        total_co2_ton_per_year=total_co2,
        captured_co2_ton_per_year=captured_co2,
        vented_co2_ton_per_year=vented_co2,
        methanol_ton_per_year=methanol_actual,
        h2_required_ton_per_year=h2_required,
        electrolyzer_required_mw=electrolyzer_mw,
        gross_revenue_usd_per_year=gross_revenue,
        lcom_usd_per_ton=lcom,
        npv_usd=npv,
        irr=irr,
        payback_years=payback,
        missing_inputs=sorted(set(missing_inputs)),
        assumption_snapshot={
            "scenario": _snapshot_fields(
                scenario,
                [
                    "scenario_name",
                    "scheme",
                    "capture_rate",
                    "process_efficiency",
                    "data_status",
                    "confidence_level",
                ],
            ),
            "financial_assumption": _snapshot_fields(
                financial_assumption,
                [
                    "methanol_price_usd_per_ton",
                    "grey_methanol_price_usd_per_ton",
                    "hydrogen_price_usd_per_kg",
                    "electricity_price_usd_per_kwh",
                    "carbon_credit_price_idr_per_ton",
                    "exchange_rate_idr_usd",
                    "discount_rate",
                    "tax_rate",
                    "capex_capture_usd",
                    "capex_electrolyzer_usd",
                    "capex_methanol_plant_usd",
                    "capex_storage_port_usd",
                    "opex_percent_capex",
                    "data_status",
                    "confidence_level",
                ],
            ),
            "plant": _snapshot_fields(
                plant,
                ["plant_name", "unit_name", "operating_days_per_year", "data_status", "confidence_level"],
            ),
        },
        calculation_version=CALCULATION_VERSION,
        confidence_level=confidence,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

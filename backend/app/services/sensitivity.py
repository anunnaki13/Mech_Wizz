import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BusinessScenario, FinancialAssumption, Plant, ScenarioResult, SensitivityResult
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
)
from app.services.scoring import latest_scenario_result


DEFAULT_SENSITIVITY_VARIABLES = [
    "h2_price",
    "electricity_price",
    "methanol_price",
    "capex",
    "capture_rate",
    "plant_availability",
    "carbon_credit_price",
    "exchange_rate",
]


class SensitivityInputError(ValueError):
    pass


@dataclass(frozen=True)
class FinancialOutputs:
    irr: float | None
    npv_usd: float | None
    lcom_usd_per_ton: float | None
    payback_years: float | None
    missing_inputs: list[str]
    warnings: list[str]


def _snapshot(record: object | None, fields: list[str]) -> dict[str, Any] | None:
    if record is None:
        return None
    return {field: getattr(record, field) for field in fields}


def _multiply(value: float | int | None, multiplier: float) -> float | None:
    return None if value is None else float(value) * multiplier


def _scenario_base_value(
    variable: str,
    plant: Plant,
    scenario: BusinessScenario,
    financial_assumption: FinancialAssumption | None,
) -> float | None:
    if financial_assumption is None and variable not in {"capture_rate", "plant_availability"}:
        return None
    if variable == "h2_price":
        return financial_assumption.hydrogen_price_usd_per_kg if financial_assumption else None
    if variable == "electricity_price":
        return financial_assumption.electricity_price_usd_per_kwh if financial_assumption else None
    if variable == "methanol_price":
        return financial_assumption.methanol_price_usd_per_ton if financial_assumption else None
    if variable == "capex" and financial_assumption:
        return calculate_total_capex_usd(
            financial_assumption.capex_capture_usd,
            financial_assumption.capex_electrolyzer_usd,
            financial_assumption.capex_methanol_plant_usd,
            financial_assumption.capex_storage_port_usd,
        )
    if variable == "capture_rate":
        return scenario.capture_rate
    if variable == "plant_availability":
        return float(plant.operating_days_per_year) if plant.operating_days_per_year is not None else None
    if variable == "carbon_credit_price":
        return financial_assumption.carbon_credit_price_idr_per_ton if financial_assumption else None
    if variable == "exchange_rate":
        return financial_assumption.exchange_rate_idr_usd if financial_assumption else None
    return None


def _variant_outputs(
    *,
    variable: str | None,
    multiplier: float,
    plant: Plant,
    scenario: BusinessScenario,
    result: ScenarioResult,
    financial_assumption: FinancialAssumption | None,
) -> FinancialOutputs:
    missing_inputs: list[str] = []
    warnings: list[str] = []
    if financial_assumption is None:
        return FinancialOutputs(
            irr=None,
            npv_usd=None,
            lcom_usd_per_ton=None,
            payback_years=None,
            missing_inputs=["financial_assumptions"],
            warnings=["Financial assumptions are required for sensitivity outputs."],
        )

    required_fields = [
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
    ]
    for field in required_fields:
        if getattr(financial_assumption, field) is None:
            missing_inputs.append(f"financial_assumptions.{field}")

    methanol_price = financial_assumption.methanol_price_usd_per_ton
    carbon_credit_price = financial_assumption.carbon_credit_price_idr_per_ton
    exchange_rate = financial_assumption.exchange_rate_idr_usd
    h2_price = financial_assumption.hydrogen_price_usd_per_kg
    electricity_price = financial_assumption.electricity_price_usd_per_kwh
    capex_capture = financial_assumption.capex_capture_usd
    capex_electrolyzer = financial_assumption.capex_electrolyzer_usd
    capex_methanol = financial_assumption.capex_methanol_plant_usd
    capex_storage = financial_assumption.capex_storage_port_usd
    operating_days = float(plant.operating_days_per_year) if plant.operating_days_per_year is not None else None
    capture_rate = scenario.capture_rate if scenario.capture_rate is not None else 0.85

    if variable == "h2_price":
        h2_price = _multiply(h2_price, multiplier)
    elif variable == "electricity_price":
        electricity_price = _multiply(electricity_price, multiplier)
    elif variable == "methanol_price":
        methanol_price = _multiply(methanol_price, multiplier)
    elif variable == "capex":
        capex_capture = _multiply(capex_capture, multiplier)
        capex_electrolyzer = _multiply(capex_electrolyzer, multiplier)
        capex_methanol = _multiply(capex_methanol, multiplier)
        capex_storage = _multiply(capex_storage, multiplier)
    elif variable == "capture_rate":
        capture_rate = max(0.0, min(1.0, capture_rate * multiplier))
    elif variable == "plant_availability":
        operating_days = _multiply(operating_days, multiplier)
    elif variable == "carbon_credit_price":
        carbon_credit_price = _multiply(carbon_credit_price, multiplier)
    elif variable == "exchange_rate":
        exchange_rate = _multiply(exchange_rate, multiplier)

    total_co2 = result.total_co2_ton_per_year
    if variable == "plant_availability":
        total_co2 = _multiply(total_co2, multiplier)
    captured_co2 = calculate_captured_co2_ton_year(total_co2, capture_rate)
    methanol_theoretical = calculate_methanol_theoretical_ton_year(captured_co2)
    process_efficiency = scenario.process_efficiency if scenario.process_efficiency is not None else DEFAULT_PROCESS_EFFICIENCY
    methanol_actual = calculate_methanol_actual_ton_year(methanol_theoretical, process_efficiency)
    h2_required = calculate_h2_required_ton_year(methanol_actual)
    electrolyzer_mw = calculate_electrolyzer_mw(h2_required, operating_days)

    carbon_price_usd = calculate_carbon_credit_price_usd_per_ton(carbon_credit_price, exchange_rate)
    gross_revenue = calculate_gross_revenue_usd_per_year(
        methanol_actual,
        methanol_price,
        captured_co2,
        carbon_price_usd,
    )
    total_capex = calculate_total_capex_usd(capex_capture, capex_electrolyzer, capex_methanol, capex_storage)
    annualized_capex = calculate_annualized_capex_usd(
        total_capex,
        financial_assumption.discount_rate,
        DEFAULT_PROJECT_LIFE_YEARS,
    )
    annual_opex = calculate_annual_opex_usd(total_capex, financial_assumption.opex_percent_capex)
    annual_h2_cost = calculate_h2_cost_usd_per_year(h2_required, h2_price)
    annual_electricity_cost = calculate_electricity_cost_usd_per_year(
        electrolyzer_mw,
        operating_days,
        electricity_price,
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
    npv = calculate_npv(total_capex, annual_cashflow, financial_assumption.discount_rate, DEFAULT_PROJECT_LIFE_YEARS)
    irr = calculate_project_irr(total_capex, annual_cashflow, DEFAULT_PROJECT_LIFE_YEARS)
    payback = calculate_payback_years(total_capex, annual_cashflow)

    if missing_inputs:
        warnings.append("Financial assumptions are incomplete; sensitivity output fields may be null.")
    if annual_cashflow is not None and annual_cashflow <= 0:
        warnings.append("Annual cashflow is non-positive; IRR and payback may be unavailable.")
    if any(value is None for value in [lcom, npv, irr, payback]):
        warnings.append("One or more economics outputs could not be calculated.")

    return FinancialOutputs(
        irr=irr,
        npv_usd=npv,
        lcom_usd_per_ton=lcom,
        payback_years=payback,
        missing_inputs=sorted(set(missing_inputs)),
        warnings=sorted(set(warnings)),
    )


def _impact_score(base: FinancialOutputs, low: FinancialOutputs, high: FinancialOutputs) -> float:
    if base.irr is not None and (low.irr is not None or high.irr is not None):
        deltas = [abs(value - base.irr) for value in [low.irr, high.irr] if value is not None]
        return round(max(deltas, default=0.0), 6)
    if base.npv_usd not in (None, 0) and (low.npv_usd is not None or high.npv_usd is not None):
        deltas = [abs(value - base.npv_usd) / abs(base.npv_usd) for value in [low.npv_usd, high.npv_usd] if value is not None]
        return round(max(deltas, default=0.0), 6)
    if base.lcom_usd_per_ton not in (None, 0) and (
        low.lcom_usd_per_ton is not None or high.lcom_usd_per_ton is not None
    ):
        deltas = [
            abs(value - base.lcom_usd_per_ton) / abs(base.lcom_usd_per_ton)
            for value in [low.lcom_usd_per_ton, high.lcom_usd_per_ton]
            if value is not None
        ]
        return round(max(deltas, default=0.0), 6)
    return 0.0


def run_sensitivity_analysis(
    db: Session,
    *,
    scenario_id: str,
    plant_id: str | None = None,
    variables: list[str] | None = None,
    low_multiplier: float = 0.80,
    high_multiplier: float = 1.20,
) -> tuple[str, list[SensitivityResult]]:
    scenario = db.get(BusinessScenario, scenario_id)
    if scenario is None:
        raise SensitivityInputError("Scenario not found")
    plant = db.get(Plant, plant_id or scenario.plant_id)
    if plant is None or plant.id != scenario.plant_id:
        raise SensitivityInputError("Plant not found for scenario")
    result = latest_scenario_result(db, scenario.id)
    if result is None:
        raise SensitivityInputError("Run scenario simulation before sensitivity analysis")

    financial_assumption = db.scalar(
        select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id)
    )
    run_id = str(uuid.uuid4())
    variable_names = variables or DEFAULT_SENSITIVITY_VARIABLES
    records: list[SensitivityResult] = []
    base = _variant_outputs(
        variable=None,
        multiplier=1.0,
        plant=plant,
        scenario=scenario,
        result=result,
        financial_assumption=financial_assumption,
    )

    for variable in variable_names:
        low = _variant_outputs(
            variable=variable,
            multiplier=low_multiplier,
            plant=plant,
            scenario=scenario,
            result=result,
            financial_assumption=financial_assumption,
        )
        high = _variant_outputs(
            variable=variable,
            multiplier=high_multiplier,
            plant=plant,
            scenario=scenario,
            result=result,
            financial_assumption=financial_assumption,
        )
        missing_inputs = sorted(set(base.missing_inputs + low.missing_inputs + high.missing_inputs))
        warnings = sorted(set(base.warnings + low.warnings + high.warnings))
        confidence = "low" if missing_inputs or warnings else scenario.confidence_level
        base_value = _scenario_base_value(variable, plant, scenario, financial_assumption)
        record = SensitivityResult(
            run_id=run_id,
            plant_id=plant.id,
            scenario_id=scenario.id,
            scenario_result_id=result.id,
            variable_name=variable,
            low_input_value=_multiply(base_value, low_multiplier),
            base_input_value=base_value,
            high_input_value=_multiply(base_value, high_multiplier),
            low_irr=low.irr,
            base_irr=base.irr,
            high_irr=high.irr,
            low_npv_usd=low.npv_usd,
            base_npv_usd=base.npv_usd,
            high_npv_usd=high.npv_usd,
            low_lcom_usd_per_ton=low.lcom_usd_per_ton,
            base_lcom_usd_per_ton=base.lcom_usd_per_ton,
            high_lcom_usd_per_ton=high.lcom_usd_per_ton,
            impact_score=_impact_score(base, low, high),
            missing_inputs=missing_inputs,
            warnings=warnings,
            assumption_snapshot={
                "scenario": _snapshot(
                    scenario,
                    ["scenario_name", "scheme", "capture_rate", "process_efficiency", "data_status", "confidence_level"],
                ),
                "financial_assumption": _snapshot(
                    financial_assumption,
                    [
                        "methanol_price_usd_per_ton",
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
            },
            confidence_level=confidence,
        )
        db.add(record)
        records.append(record)

    db.commit()
    for record in records:
        db.refresh(record)
    return run_id, records


def list_sensitivity_results(
    db: Session,
    *,
    scenario_id: str,
    plant_id: str | None = None,
) -> list[SensitivityResult]:
    query = select(SensitivityResult).where(SensitivityResult.scenario_id == scenario_id)
    if plant_id:
        query = query.where(SensitivityResult.plant_id == plant_id)
    return list(
        db.scalars(
            query.order_by(
                SensitivityResult.created_at.desc(),
                SensitivityResult.run_id.desc(),
                SensitivityResult.impact_score.desc(),
                SensitivityResult.variable_name,
            )
        )
    )

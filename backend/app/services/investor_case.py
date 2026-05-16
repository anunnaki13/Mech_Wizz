from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    BusinessScenario,
    EmissionTest,
    FinancialAssumption,
    HydrogenStrategy,
    Plant,
    ScenarioResult,
    SensitivityResult,
    SiteReadiness,
    UnitScoringResult,
)
from app.services.calculations.financial import calculate_carbon_credit_price_usd_per_ton
from app.services.scoring import derive_data_gaps, format_recommended_scheme


class InvestorCaseInputError(ValueError):
    pass


CAPEX_FIELDS = [
    ("capture", "capex_capture_usd", "Carbon capture"),
    ("electrolyzer", "capex_electrolyzer_usd", "Electrolyzer"),
    ("methanol_plant", "capex_methanol_plant_usd", "Methanol plant"),
    ("storage_port", "capex_storage_port_usd", "Storage and port"),
]


def _record_fields(record: object, fields: list[str]) -> dict[str, Any]:
    return {field: getattr(record, field) for field in fields}


def _latest_scenario_result(db: Session, scenario_id: str) -> ScenarioResult | None:
    return db.scalar(
        select(ScenarioResult)
        .where(ScenarioResult.scenario_id == scenario_id)
        .order_by(ScenarioResult.created_at.desc(), ScenarioResult.id.desc())
    )


def _latest_scoring_result(db: Session, plant_id: str, scenario_id: str) -> UnitScoringResult | None:
    return db.scalar(
        select(UnitScoringResult)
        .where(UnitScoringResult.plant_id == plant_id, UnitScoringResult.scenario_id == scenario_id)
        .order_by(UnitScoringResult.created_at.desc(), UnitScoringResult.id.desc())
    )


def _latest_sensitivity_run(db: Session, plant_id: str, scenario_id: str) -> list[SensitivityResult]:
    latest = db.scalar(
        select(SensitivityResult)
        .where(SensitivityResult.plant_id == plant_id, SensitivityResult.scenario_id == scenario_id)
        .order_by(SensitivityResult.created_at.desc(), SensitivityResult.run_id.desc())
    )
    if latest is None:
        return []
    return list(
        db.scalars(
            select(SensitivityResult)
            .where(SensitivityResult.run_id == latest.run_id)
            .order_by(SensitivityResult.impact_score.desc(), SensitivityResult.variable_name)
        )
    )


def _financial_assumption(db: Session, scenario_id: str) -> FinancialAssumption | None:
    return db.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario_id))


def _select_scenario(db: Session, plant: Plant, scenario_id: str | None) -> BusinessScenario:
    query = select(BusinessScenario).where(BusinessScenario.plant_id == plant.id)
    if scenario_id:
        query = query.where(BusinessScenario.id == scenario_id)
    scenario = db.scalar(query.order_by(BusinessScenario.created_at.desc(), BusinessScenario.id.desc()))
    if scenario is None:
        raise InvestorCaseInputError("Scenario not found for plant")
    return scenario


def _capex_structure(
    scenario: BusinessScenario,
    financial_assumption: FinancialAssumption | None,
) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    components = []
    total = 0.0
    has_missing = False
    for key, field, label in CAPEX_FIELDS:
        amount = getattr(financial_assumption, field) if financial_assumption else None
        if amount is None:
            has_missing = True
        else:
            total += amount
        components.append(
            {
                "key": key,
                "label": label,
                "amount_usd": amount,
                "data_status": financial_assumption.data_status if financial_assumption else "unknown",
            }
        )
    if financial_assumption is None:
        warnings.append("Financial assumptions are missing.")
    if has_missing:
        warnings.append("CAPEX structure is incomplete; financial KPIs remain indicative or unavailable.")

    total_value = None if has_missing else total
    return (
        {
            "total_capex_usd": total_value,
            "components": components,
            "pln_responsibility_percent": scenario.pln_capex_responsibility_percent,
            "partner_responsibility_percent": scenario.partner_capex_responsibility_percent,
            "model": format_recommended_scheme(scenario.scheme),
            "is_complete": not has_missing,
        },
        warnings,
    )


def _revenue_mix(
    result: ScenarioResult | None,
    financial_assumption: FinancialAssumption | None,
) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    methanol_revenue = None
    carbon_revenue = None
    if result is None:
        warnings.append("Scenario simulation result is missing.")
    if financial_assumption is None:
        warnings.append("Financial assumptions are missing.")

    if result and financial_assumption:
        if result.methanol_ton_per_year is not None and financial_assumption.methanol_price_usd_per_ton is not None:
            methanol_revenue = result.methanol_ton_per_year * financial_assumption.methanol_price_usd_per_ton
        carbon_price_usd = calculate_carbon_credit_price_usd_per_ton(
            financial_assumption.carbon_credit_price_idr_per_ton,
            financial_assumption.exchange_rate_idr_usd,
        )
        if result.captured_co2_ton_per_year is not None and carbon_price_usd is not None:
            carbon_revenue = result.captured_co2_ton_per_year * carbon_price_usd

    if methanol_revenue is None:
        warnings.append("Methanol revenue cannot be calculated from current assumptions.")
    if carbon_revenue is None:
        warnings.append("Carbon credit revenue cannot be calculated from current assumptions.")

    service_revenue = None
    total = sum(value for value in [methanol_revenue, carbon_revenue, service_revenue] if value is not None)
    return (
        [
            {"label": "E-methanol sales", "value_usd_per_year": methanol_revenue, "share": None},
            {"label": "Carbon credits", "value_usd_per_year": carbon_revenue, "share": None},
            {"label": "Land, utilities, and port services", "value_usd_per_year": service_revenue, "share": None},
        ],
        warnings + ([] if total > 0 else ["Revenue mix is incomplete."]),
    )


def _scenario_comparison(db: Session, plant_id: str) -> list[dict[str, Any]]:
    rows = []
    scenarios = list(
        db.scalars(
            select(BusinessScenario)
            .where(BusinessScenario.plant_id == plant_id)
            .order_by(BusinessScenario.scheme, BusinessScenario.created_at.desc())
        )
    )
    by_scheme = {scenario.scheme: scenario for scenario in scenarios}
    for scheme in ["access", "align", "augment"]:
        scenario = by_scheme.get(scheme)
        if scenario is None:
            rows.append(
                {
                    "scheme": scheme,
                    "scenario_id": None,
                    "scenario_name": None,
                    "available": False,
                    "irr": None,
                    "npv_usd": None,
                    "lcom_usd_per_ton": None,
                    "payback_years": None,
                    "composite_score": None,
                    "confidence_level": "unknown",
                }
            )
            continue
        result = _latest_scenario_result(db, scenario.id)
        scoring = _latest_scoring_result(db, plant_id, scenario.id)
        rows.append(
            {
                "scheme": scheme,
                "scenario_id": scenario.id,
                "scenario_name": scenario.scenario_name,
                "available": True,
                "irr": result.irr if result else None,
                "npv_usd": result.npv_usd if result else None,
                "lcom_usd_per_ton": result.lcom_usd_per_ton if result else None,
                "payback_years": result.payback_years if result else None,
                "composite_score": scoring.composite_score if scoring else None,
                "confidence_level": result.confidence_level if result else "unknown",
            }
        )
    return rows


def _recommendation_for_gap(gap: dict[str, str]) -> str:
    module = gap.get("module")
    if module == "hydrogen":
        return "Request indicative proposal from electrolyzer or hydrogen partner."
    if module == "capex":
        return "Use benchmark for screening, validate during pre-FEED."
    if module == "land":
        return "Confirm available land with site engineering team."
    if module == "geo_location":
        return "Confirm exact unit and project boundary coordinates."
    if module == "financial":
        return "Complete financial assumptions before presenting financial KPIs."
    return "Validate the missing input with the accountable data owner."


def _risk_matrix(gaps: list[dict[str, str]], sensitivity: list[SensitivityResult]) -> list[dict[str, Any]]:
    risks = []
    for gap in gaps[:5]:
        risks.append(
            {
                "risk": gap["name"],
                "impact": gap["impact"],
                "priority": gap["priority"],
                "mitigation": _recommendation_for_gap(gap),
                "source": gap["module"],
            }
        )
    dominant = sensitivity[0] if sensitivity else None
    if dominant is not None:
        risks.append(
            {
                "risk": f"{dominant.variable_name} sensitivity",
                "impact": "high" if dominant.impact_score > 0.05 else "medium",
                "priority": "urgent" if dominant.impact_score > 0.05 else "medium",
                "mitigation": "Validate the dominant sensitivity driver before investment committee review.",
                "source": "sensitivity",
            }
        )
    return risks


def _confidence_level(
    result: ScenarioResult | None,
    scoring: UnitScoringResult | None,
    gaps: list[dict[str, str]],
) -> str:
    if result is None or scoring is None:
        return "unknown"
    if any(gap["priority"] == "urgent" for gap in gaps):
        return "low"
    if result.confidence_level == "low" or scoring.confidence_score < 0.45:
        return "low"
    if result.confidence_level == "high" and scoring.confidence_score >= 0.75:
        return "high"
    return "medium"


def _thesis_flow(plant: Plant, scenario: BusinessScenario, scoring: UnitScoringResult | None) -> list[dict[str, str]]:
    score_label = f"{scoring.composite_score:.2f}" if scoring else "not scored"
    return [
        {
            "section": "Investment thesis",
            "stage": "Assets & Advantages",
            "summary": f"{plant.plant_name} combines PLN NP ownership context, existing generation assets, and CO2 source potential.",
        },
        {
            "section": "Investment thesis",
            "stage": "Partner Solution",
            "summary": f"{format_recommended_scheme(scenario.scheme)} frames partner and PLN CAPEX responsibility for an early pilot case.",
        },
        {
            "section": "Investment thesis",
            "stage": "Market Access",
            "summary": "E-methanol and carbon credit revenue are separated so market assumptions remain visible.",
        },
        {
            "section": "Investment thesis",
            "stage": "Output & Value",
            "summary": f"The current composite score is {score_label}; economics remain indicative until missing assumptions are validated.",
        },
    ]


def _roadmap() -> list[dict[str, str]]:
    return [
        {"step": "1", "title": "Pilot & Feasibility", "description": "Validate site data, CAPEX, H2 supply, and offtake assumptions."},
        {"step": "2", "title": "Financial Close", "description": "Lock partner structure, revenue contracts, and investment case."},
        {"step": "3", "title": "Construction", "description": "Execute capture, H2, methanol, storage, and integration scope."},
        {"step": "4", "title": "COD Phase 1", "description": "Operate the first production train and monitor performance."},
        {"step": "5", "title": "Scale-Up", "description": "Replicate the model across ranked PLN NP candidate sites."},
    ]


def _why_this_wins(plant: Plant, scoring: UnitScoringResult | None) -> list[str]:
    wins = [
        "First-mover e-methanol platform inside a PLN NP asset base.",
        "Deterministic screening keeps technical and financial assumptions auditable.",
        "Partner-financed business schemes can be compared without changing source data.",
        "Digital scoring, sensitivity, and data gaps reduce early diligence ambiguity.",
    ]
    if plant.province:
        wins.insert(1, f"{plant.province} location can be positioned as the first pilot reference.")
    if scoring and scoring.rank_position == 1:
        wins.insert(0, "Current ranking marks this unit as the leading pilot candidate.")
    return wins


def build_investor_case(
    db: Session,
    *,
    plant_id: str | None = None,
    scenario_id: str | None = None,
) -> dict[str, Any]:
    if plant_id:
        plant = db.get(Plant, plant_id)
    elif scenario_id:
        scenario_for_plant = db.get(BusinessScenario, scenario_id)
        plant = db.get(Plant, scenario_for_plant.plant_id) if scenario_for_plant else None
    else:
        plant = db.scalar(select(Plant).order_by(Plant.created_at.desc(), Plant.id.desc()))
    if plant is None:
        raise InvestorCaseInputError("Plant not found")

    scenario = _select_scenario(db, plant, scenario_id)
    result = _latest_scenario_result(db, scenario.id)
    scoring = _latest_scoring_result(db, plant.id, scenario.id)
    sensitivity = _latest_sensitivity_run(db, plant.id, scenario.id)
    financial_assumption = _financial_assumption(db, scenario.id)
    site_readiness = db.scalar(select(SiteReadiness).where(SiteReadiness.plant_id == plant.id))
    hydrogen_strategy = db.scalar(select(HydrogenStrategy).where(HydrogenStrategy.plant_id == plant.id))
    emission_tests = list(db.scalars(select(EmissionTest).where(EmissionTest.plant_id == plant.id)))

    data_gaps = derive_data_gaps(plant, result, site_readiness, hydrogen_strategy, financial_assumption)
    enriched_gaps = [
        {
            **gap,
            "missing_data": gap["name"],
            "recommendation": _recommendation_for_gap(gap),
            "status": "open",
        }
        for gap in data_gaps
    ]
    capex_structure, capex_warnings = _capex_structure(scenario, financial_assumption)
    revenue_mix, revenue_warnings = _revenue_mix(result, financial_assumption)
    warnings = sorted(
        set(
            capex_warnings
            + revenue_warnings
            + ([] if result else ["Run scenario simulation before presenting investor KPIs."])
            + ([] if scoring else ["Recalculate scoring before presenting investor ranking context."])
        )
    )
    confidence = _confidence_level(result, scoring, enriched_gaps)
    dominant_sensitivity = sensitivity[0] if sensitivity else None

    return {
        "plant": _record_fields(
            plant,
            [
                "id",
                "plant_name",
                "unit_name",
                "province",
                "city",
                "capacity_mw",
                "fuel_type",
                "owner",
                "data_status",
                "confidence_level",
            ],
        ),
        "scenario": _record_fields(
            scenario,
            [
                "id",
                "plant_id",
                "scenario_name",
                "scheme",
                "pln_ownership_percent",
                "partner_capex_responsibility_percent",
                "pln_capex_responsibility_percent",
                "revenue_model",
                "data_status",
                "confidence_level",
            ],
        ),
        "kpis": {
            "project_irr": result.irr if result else None,
            "estimated_npv_usd": result.npv_usd if result else None,
            "lcom_usd_per_ton": result.lcom_usd_per_ton if result else None,
            "payback_years": result.payback_years if result else None,
            "e_methanol_capacity_tpy": result.methanol_ton_per_year if result else None,
            "co2_abatement_tpy": result.captured_co2_ton_per_year if result else None,
            "total_co2_tpy": result.total_co2_ton_per_year if result else None,
            "composite_score": scoring.composite_score if scoring else None,
            "opportunity_score": scoring.opportunity_score if scoring else None,
            "readiness_score": scoring.readiness_score if scoring else None,
            "confidence_score": scoring.confidence_score if scoring else None,
            "rank_position": scoring.rank_position if scoring else None,
        },
        "capex_structure": capex_structure,
        "revenue_mix": revenue_mix,
        "scenario_comparison": _scenario_comparison(db, plant.id),
        "thesis_flow": _thesis_flow(plant, scenario, scoring),
        "risks": _risk_matrix(enriched_gaps, sensitivity),
        "roadmap": _roadmap(),
        "why_this_wins": _why_this_wins(plant, scoring),
        "data_gaps": enriched_gaps,
        "sensitivity": {
            "run_id": dominant_sensitivity.run_id,
            "dominant_driver": dominant_sensitivity.variable_name,
            "impact_score": dominant_sensitivity.impact_score,
            "confidence_level": dominant_sensitivity.confidence_level,
        }
        if dominant_sensitivity
        else None,
        "confidence_level": confidence,
        "warnings": warnings,
        "data_quality": {
            "input_records": {
                "emission_tests": len(emission_tests),
                "site_readiness": site_readiness is not None,
                "hydrogen_strategy": hydrogen_strategy is not None,
                "financial_assumption": financial_assumption is not None,
            },
            "output_confidence": {
                "scenario_result": result.confidence_level if result else "unknown",
                "scoring": "low" if scoring is None or scoring.confidence_score < 0.45 else "medium",
                "investor_case": confidence,
            },
        },
    }

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
    SiteReadiness,
    UnitScoringResult,
)
from app.services.scoring import confidence_label, derive_data_gaps


def _record_dict(record: object | None, fields: list[str]) -> dict[str, Any] | None:
    if record is None:
        return None
    return {field: getattr(record, field) for field in fields}


def _latest_scenario_for_plant(db: Session, plant_id: str, scenario_id: str | None) -> BusinessScenario | None:
    query = select(BusinessScenario).where(BusinessScenario.plant_id == plant_id)
    if scenario_id:
        query = query.where(BusinessScenario.id == scenario_id)
    return db.scalar(query.order_by(BusinessScenario.created_at.desc(), BusinessScenario.id.desc()))


def _latest_result_for_scenario(db: Session, scenario_id: str) -> ScenarioResult | None:
    return db.scalar(
        select(ScenarioResult)
        .where(ScenarioResult.scenario_id == scenario_id)
        .order_by(ScenarioResult.created_at.desc(), ScenarioResult.id.desc())
    )


def _latest_scoring_for_scenario(db: Session, plant_id: str, scenario_id: str) -> UnitScoringResult | None:
    return db.scalar(
        select(UnitScoringResult)
        .where(UnitScoringResult.plant_id == plant_id, UnitScoringResult.scenario_id == scenario_id)
        .order_by(UnitScoringResult.created_at.desc(), UnitScoringResult.id.desc())
    )


def build_unit_profile(db: Session, plant_id: str, scenario_id: str | None = None) -> dict[str, Any] | None:
    plant = db.get(Plant, plant_id)
    if plant is None:
        return None

    scenario = _latest_scenario_for_plant(db, plant.id, scenario_id)
    result = _latest_result_for_scenario(db, scenario.id) if scenario else None
    scoring = _latest_scoring_for_scenario(db, plant.id, scenario.id) if scenario else None
    site_readiness = db.scalar(select(SiteReadiness).where(SiteReadiness.plant_id == plant.id))
    hydrogen_strategy = db.scalar(select(HydrogenStrategy).where(HydrogenStrategy.plant_id == plant.id))
    financial_assumption = (
        db.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id))
        if scenario
        else None
    )
    emission_tests = list(db.scalars(select(EmissionTest).where(EmissionTest.plant_id == plant.id)))
    data_gaps = derive_data_gaps(plant, result, site_readiness, hydrogen_strategy, financial_assumption)

    latest_scoring = None
    score_breakdown: dict[str, Any] = {}
    if scoring is not None:
        latest_scoring = {
            "id": scoring.id,
            "rank_position": scoring.rank_position,
            "opportunity_score": scoring.opportunity_score,
            "readiness_score": scoring.readiness_score,
            "confidence_score": scoring.confidence_score,
            "composite_score": scoring.composite_score,
            "heatmap_weight": scoring.component_scores.get("heatmap_weight", scoring.composite_score),
            "recommended_scheme": scoring.recommended_scheme,
            "key_bottleneck": scoring.key_bottleneck,
            "data_gap_count": scoring.data_gap_count,
            "scoring_version": scoring.scoring_version,
            "created_at": scoring.created_at,
        }
        score_breakdown = scoring.component_scores

    return {
        "plant": {
            "id": plant.id,
            "plant_name": plant.plant_name,
            "unit_name": plant.unit_name,
            "province": plant.province,
            "city": plant.city,
            "latitude": plant.latitude,
            "longitude": plant.longitude,
            "capacity_mw": plant.capacity_mw,
            "fuel_type": plant.fuel_type,
            "status": plant.status,
            "owner": plant.owner,
            "data_status": plant.data_status,
            "confidence_level": plant.confidence_level,
        },
        "scenario": _record_dict(
            scenario,
            [
                "id",
                "scenario_name",
                "scheme",
                "capture_rate",
                "process_efficiency",
                "data_status",
                "confidence_level",
            ],
        ),
        "latest_result": _record_dict(
            result,
            [
                "id",
                "total_co2_ton_per_year",
                "captured_co2_ton_per_year",
                "vented_co2_ton_per_year",
                "methanol_ton_per_year",
                "h2_required_ton_per_year",
                "electrolyzer_required_mw",
                "gross_revenue_usd_per_year",
                "lcom_usd_per_ton",
                "npv_usd",
                "irr",
                "payback_years",
                "missing_inputs",
                "calculation_version",
                "confidence_level",
                "created_at",
            ],
        ),
        "latest_scoring": latest_scoring,
        "score_breakdown": score_breakdown,
        "data_gaps": data_gaps,
        "confidence_labels": {
            "plant": plant.confidence_level,
            "scenario": scenario.confidence_level if scenario else "unknown",
            "simulation": result.confidence_level if result else "unknown",
            "scoring": confidence_label(scoring.confidence_score) if scoring else "Unknown",
            "emission_tests": "available" if emission_tests else "missing",
            "site_readiness": site_readiness.confidence_level if site_readiness else "unknown",
            "hydrogen_strategy": hydrogen_strategy.confidence_level if hydrogen_strategy else "unknown",
        },
    }

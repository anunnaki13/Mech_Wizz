from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    BusinessScenario,
    DataGap,
    EmissionTest,
    FinancialAssumption,
    HydrogenStrategy,
    Plant,
    ScenarioResult,
    SensitivityResult,
    SiteReadiness,
    UnitScoringResult,
)
from app.services.investor_case import _recommendation_for_gap
from app.services.scoring import derive_data_gaps


def _latest_result(db: Session, scenario_id: str) -> ScenarioResult | None:
    return db.scalar(
        select(ScenarioResult)
        .where(ScenarioResult.scenario_id == scenario_id)
        .order_by(ScenarioResult.created_at.desc(), ScenarioResult.id.desc())
    )


def _latest_scoring(db: Session, plant_id: str, scenario_id: str) -> UnitScoringResult | None:
    return db.scalar(
        select(UnitScoringResult)
        .where(UnitScoringResult.plant_id == plant_id, UnitScoringResult.scenario_id == scenario_id)
        .order_by(UnitScoringResult.created_at.desc(), UnitScoringResult.id.desc())
    )


def _latest_sensitivity(db: Session, plant_id: str, scenario_id: str) -> SensitivityResult | None:
    return db.scalar(
        select(SensitivityResult)
        .where(SensitivityResult.plant_id == plant_id, SensitivityResult.scenario_id == scenario_id)
        .order_by(SensitivityResult.created_at.desc(), SensitivityResult.id.desc())
    )


def sync_data_gaps(db: Session, plant_id: str, scenario_id: str | None = None) -> list[DataGap]:
    plant = db.get(Plant, plant_id)
    if plant is None:
        return []
    scenario = db.get(BusinessScenario, scenario_id) if scenario_id else None
    result = _latest_result(db, scenario.id) if scenario else None
    site_readiness = db.scalar(select(SiteReadiness).where(SiteReadiness.plant_id == plant.id))
    hydrogen_strategy = db.scalar(select(HydrogenStrategy).where(HydrogenStrategy.plant_id == plant.id))
    financial_assumption = (
        db.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id))
        if scenario
        else None
    )
    gaps = derive_data_gaps(plant, result, site_readiness, hydrogen_strategy, financial_assumption)
    records: list[DataGap] = []
    for gap in gaps:
        existing = db.scalar(
            select(DataGap).where(
                DataGap.plant_id == plant.id,
                DataGap.scenario_id == (scenario.id if scenario else None),
                DataGap.source_module == gap["module"],
                DataGap.missing_data_name == gap["name"],
            )
        )
        if existing is None:
            existing = DataGap(
                plant_id=plant.id,
                scenario_id=scenario.id if scenario else None,
                source_module=gap["module"],
                missing_data_name=gap["name"],
                impact_level=gap["impact"],
                priority_level=gap["priority"],
                recommendation=_recommendation_for_gap(gap),
                status="open",
            )
            db.add(existing)
        else:
            existing.impact_level = gap["impact"]
            existing.priority_level = gap["priority"]
            existing.recommendation = _recommendation_for_gap(gap)
            existing.status = "open"
        records.append(existing)
    db.commit()
    for record in records:
        db.refresh(record)
    return records


def build_data_quality_summary(db: Session, plant_id: str, scenario_id: str | None = None) -> dict:
    plant = db.get(Plant, plant_id)
    scenario = db.get(BusinessScenario, scenario_id) if scenario_id else None
    if plant is None:
        return {"plant_id": plant_id, "scenario_id": scenario_id, "input_status": {}, "output_confidence": {}, "gaps": []}

    emission_tests = list(db.scalars(select(EmissionTest).where(EmissionTest.plant_id == plant.id)))
    site_readiness = db.scalar(select(SiteReadiness).where(SiteReadiness.plant_id == plant.id))
    hydrogen_strategy = db.scalar(select(HydrogenStrategy).where(HydrogenStrategy.plant_id == plant.id))
    financial_assumption = (
        db.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id))
        if scenario
        else None
    )
    result = _latest_result(db, scenario.id) if scenario else None
    scoring = _latest_scoring(db, plant.id, scenario.id) if scenario else None
    sensitivity = _latest_sensitivity(db, plant.id, scenario.id) if scenario else None
    gaps = sync_data_gaps(db, plant.id, scenario.id if scenario else None)
    return {
        "plant_id": plant.id,
        "scenario_id": scenario.id if scenario else None,
        "input_status": {
            "plant": plant.data_status,
            "emission_tests": emission_tests[0].data_status if emission_tests else "unknown",
            "site_readiness": site_readiness.data_status if site_readiness else "unknown",
            "hydrogen_strategy": hydrogen_strategy.data_status if hydrogen_strategy else "unknown",
            "scenario": scenario.data_status if scenario else "unknown",
            "financial_assumptions": financial_assumption.data_status if financial_assumption else "unknown",
        },
        "output_confidence": {
            "scenario_result": result.confidence_level if result else "unknown",
            "scoring": "medium" if scoring and scoring.confidence_score >= 0.45 else "low",
            "sensitivity": sensitivity.confidence_level if sensitivity else "unknown",
        },
        "gaps": gaps,
    }

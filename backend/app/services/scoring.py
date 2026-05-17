import uuid
from collections.abc import Iterable
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    ApplicationSetting,
    BusinessScenario,
    EmissionTest,
    FinancialAssumption,
    HydrogenStrategy,
    Plant,
    ScenarioResult,
    SiteReadiness,
    UnitScoringResult,
)


SCORING_VERSION = "phase3-scoring-v1"
DEFAULT_COMPOSITE_WEIGHTS = {"opportunity": 0.45, "readiness": 0.35, "confidence": 0.20}
DEFAULT_HEATMAP_WEIGHTS = {
    "opportunity": 0.45,
    "readiness": 0.25,
    "economic_return": 0.20,
    "confidence": 0.10,
}


def _coerce_weight_group(value: object, group_key: str, fallback: dict[str, float]) -> dict[str, float]:
    if not isinstance(value, dict):
        return fallback
    group = value.get(group_key)
    if not isinstance(group, dict):
        return fallback

    weights: dict[str, float] = {}
    for key, fallback_value in fallback.items():
        item = group.get(key, fallback_value)
        if not isinstance(item, (int, float)) or isinstance(item, bool):
            return fallback
        weights[key] = float(item)

    if abs(sum(weights.values()) - 1.0) > 0.001:
        return fallback
    return weights


def load_scoring_weights(db: Session) -> dict[str, dict[str, float]]:
    setting = db.scalar(select(ApplicationSetting).where(ApplicationSetting.key == "scoring_weights"))
    value = setting.value if setting else {}
    return {
        "composite": _coerce_weight_group(value, "composite", DEFAULT_COMPOSITE_WEIGHTS),
        "heatmap": _coerce_weight_group(value, "heatmap", DEFAULT_HEATMAP_WEIGHTS),
    }


CONFIDENCE_BY_DATA_STATUS = {
    "actual": 1.0,
    "estimated": 0.70,
    "benchmark": 0.55,
    "user_assumption": 0.50,
    "partner_supplied": 0.60,
    "unknown": 0.0,
}
CONFIDENCE_BY_LEVEL = {
    "high": 1.0,
    "medium": 0.70,
    "low": 0.35,
    "unknown": 0.0,
}


class ScoringInputError(ValueError):
    pass


def normalize_score(value: float | None, minimum: float, maximum: float) -> float:
    if value is None:
        return 0.0
    if maximum == minimum:
        return 0.5
    return round(max(0.0, min(1.0, (value - minimum) / (maximum - minimum))), 4)


def confidence_score_for_status(status: str | None) -> float:
    return CONFIDENCE_BY_DATA_STATUS.get(status or "unknown", 0.0)


def confidence_label(score: float) -> str:
    if score >= 0.75:
        return "High"
    if score >= 0.45:
        return "Medium"
    if score > 0:
        return "Low"
    return "Unknown"


def opportunity_level(score: float) -> str:
    if score >= 0.75:
        return "priority"
    if score >= 0.60:
        return "high"
    if score >= 0.40:
        return "medium"
    return "low"


def format_recommended_scheme(scheme: str | None) -> str:
    labels = {
        "access": "WIZ Access",
        "align": "WIZ Align",
        "augment": "WIZ Augment",
    }
    return labels.get((scheme or "").lower(), "WIZ Compare")


def _safe_average(values: Iterable[float]) -> float:
    values_list = list(values)
    if not values_list:
        return 0.0
    return round(sum(values_list) / len(values_list), 4)


def _text_has_any(value: str | None, tokens: tuple[str, ...]) -> bool:
    haystack = (value or "").lower()
    return any(token in haystack for token in tokens)


def _market_access_score(site_readiness: SiteReadiness | None) -> float:
    if site_readiness is None:
        return 0.25
    score = 0.25
    if site_readiness.has_port_or_jetty is True:
        score = 0.75
    if site_readiness.distance_to_port_km is not None:
        if site_readiness.distance_to_port_km <= 10:
            score = max(score, 1.0)
        elif site_readiness.distance_to_port_km <= 50:
            score = max(score, 0.75)
        elif site_readiness.distance_to_port_km <= 100:
            score = max(score, 0.50)
    if _text_has_any(site_readiness.road_access, ("good", "available", "ready", "access")):
        score = max(score, 0.65)
    return round(score, 4)


def _land_score(site_readiness: SiteReadiness | None) -> float:
    if site_readiness is None:
        return 0.0
    if site_readiness.available_land_ha is not None:
        return normalize_score(site_readiness.available_land_ha, 0, 20)
    if _text_has_any(site_readiness.land_status, ("available", "ready", "clear")):
        return 0.70
    return 0.0


def _utility_score(site_readiness: SiteReadiness | None) -> float:
    if site_readiness is None:
        return 0.0
    status_fields = (
        site_readiness.utility_readiness,
        site_readiness.power_availability,
        site_readiness.water_availability,
    )
    scores = [
        0.85
        if _text_has_any(value, ("ready", "available", "adequate", "existing"))
        else 0.45
        if value
        else 0.0
        for value in status_fields
    ]
    return _safe_average(scores)


def _permit_logistic_score(site_readiness: SiteReadiness | None, market_access_score: float) -> float:
    if site_readiness is None:
        return 0.0
    permit_risk = (site_readiness.permit_risk or "").lower()
    if "low" in permit_risk:
        permit_score = 1.0
    elif "medium" in permit_risk:
        permit_score = 0.60
    elif "high" in permit_risk:
        permit_score = 0.20
    else:
        permit_score = 0.35
    return round((permit_score * 0.55) + (market_access_score * 0.45), 4)


def _h2_strategy_score(hydrogen_strategy: HydrogenStrategy | None) -> float:
    if hydrogen_strategy is None:
        return 0.0
    score = 0.0
    if hydrogen_strategy.existing_h2_available is True:
        score = max(score, 1.0)
    if hydrogen_strategy.h2_strategy and hydrogen_strategy.h2_strategy.lower() != "unknown":
        score = max(score, 0.65)
    if hydrogen_strategy.h2_cost_usd_per_kg is not None:
        score = max(score, 0.75)
    if hydrogen_strategy.h2_readiness_score is not None:
        score = max(score, normalize_score(hydrogen_strategy.h2_readiness_score, 0, 1))
    return round(score, 4)


def _carbon_credit_score(financial_assumption: FinancialAssumption | None) -> float:
    if financial_assumption is None:
        return 0.0
    price_idr = financial_assumption.carbon_credit_price_idr_per_ton
    exchange_rate = financial_assumption.exchange_rate_idr_usd
    if price_idr is None or exchange_rate in (None, 0):
        return 0.0
    return normalize_score(price_idr / exchange_rate, 0, 20)


def _strategic_value_score(plant: Plant) -> float:
    score = 0.45
    if plant.status and plant.status.lower() == "active":
        score = max(score, 0.60)
    if plant.owner and "pln" in plant.owner.lower():
        score = max(score, 0.80)
    if plant.fuel_type and plant.fuel_type.lower() in {"coal", "gas"}:
        score = max(score, 0.70)
    return score


def _data_completeness_score(
    plant: Plant,
    result: ScenarioResult,
    site_readiness: SiteReadiness | None,
    hydrogen_strategy: HydrogenStrategy | None,
    financial_assumption: FinancialAssumption | None,
) -> float:
    fields = [
        plant.latitude,
        plant.longitude,
        plant.operating_days_per_year,
        result.total_co2_ton_per_year,
        result.methanol_ton_per_year,
        result.h2_required_ton_per_year,
        financial_assumption.methanol_price_usd_per_ton if financial_assumption else None,
        financial_assumption.hydrogen_price_usd_per_kg if financial_assumption else None,
        financial_assumption.electricity_price_usd_per_kwh if financial_assumption else None,
        financial_assumption.exchange_rate_idr_usd if financial_assumption else None,
        site_readiness.available_land_ha if site_readiness else None,
        hydrogen_strategy.h2_strategy if hydrogen_strategy else None,
    ]
    present = sum(1 for value in fields if value not in (None, "", "unknown"))
    missing_penalty = min(len(result.missing_inputs), 10) * 0.035
    return round(max(0.0, min(1.0, (present / len(fields)) - missing_penalty)), 4)


def _emission_quality_score(emission_tests: list[EmissionTest]) -> float:
    if not emission_tests:
        return 0.0
    status_score = _safe_average(confidence_score_for_status(test.data_status) for test in emission_tests)
    level_score = _safe_average(CONFIDENCE_BY_LEVEL.get(test.confidence_level, 0.0) for test in emission_tests)
    return round((status_score * 0.70) + (level_score * 0.30), 4)


def derive_data_gaps(
    plant: Plant,
    result: ScenarioResult | None,
    site_readiness: SiteReadiness | None,
    hydrogen_strategy: HydrogenStrategy | None,
    financial_assumption: FinancialAssumption | None,
) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    if plant.latitude is None or plant.longitude is None:
        gaps.append(
            {
                "module": "geo_location",
                "name": "Unit coordinate is missing",
                "impact": "high",
                "priority": "urgent",
            }
        )
    if site_readiness is None or site_readiness.available_land_ha is None:
        gaps.append(
            {
                "module": "land",
                "name": "Available land area is not confirmed",
                "impact": "medium",
                "priority": "medium",
            }
        )
    if hydrogen_strategy is None or not hydrogen_strategy.h2_strategy:
        gaps.append(
            {
                "module": "hydrogen",
                "name": "Hydrogen supply strategy is not defined",
                "impact": "very_high",
                "priority": "urgent",
            }
        )
    if financial_assumption is None:
        gaps.append(
            {
                "module": "financial",
                "name": "Financial assumptions are missing",
                "impact": "high",
                "priority": "urgent",
            }
        )
    elif financial_assumption.methanol_price_usd_per_ton is None:
        gaps.append(
            {
                "module": "market",
                "name": "Methanol price assumption is missing",
                "impact": "high",
                "priority": "urgent",
            }
        )

    if financial_assumption is not None:
        capex_fields = [
            financial_assumption.capex_capture_usd,
            financial_assumption.capex_electrolyzer_usd,
            financial_assumption.capex_methanol_plant_usd,
            financial_assumption.capex_storage_port_usd,
        ]
        if any(value is None for value in capex_fields):
            gaps.append(
                {
                    "module": "capex",
                    "name": "CAPEX package is not validated",
                    "impact": "high",
                    "priority": "urgent",
                }
            )

    if result is not None:
        for missing_input in result.missing_inputs:
            gaps.append(
                {
                    "module": "simulation",
                    "name": missing_input,
                    "impact": "medium",
                    "priority": "medium",
                }
            )

    unique: dict[tuple[str, str], dict[str, str]] = {}
    for gap in gaps:
        unique[(gap["module"], gap["name"])] = gap
    return list(unique.values())


def derive_key_bottleneck(gaps: list[dict[str, str]], scoring_components: dict[str, float]) -> str:
    urgent_modules = [gap["module"] for gap in gaps if gap["priority"] == "urgent"]
    if "hydrogen" in urgent_modules:
        return "Hydrogen supply strategy"
    if "capex" in urgent_modules:
        return "CAPEX not validated"
    if "financial" in urgent_modules:
        return "Financial assumptions"
    if "geo_location" in urgent_modules:
        return "Coordinates missing"
    if scoring_components.get("land_readiness_score", 0) < 0.30:
        return "Land readiness"
    if scoring_components.get("utility_readiness_score", 0) < 0.30:
        return "Utility readiness"
    return "No critical bottleneck identified"


def calculate_unit_scores(
    plant: Plant,
    scenario: BusinessScenario,
    result: ScenarioResult,
    emission_tests: list[EmissionTest],
    site_readiness: SiteReadiness | None,
    hydrogen_strategy: HydrogenStrategy | None,
    financial_assumption: FinancialAssumption | None,
    scoring_weights: dict[str, dict[str, float]] | None = None,
) -> dict[str, Any]:
    weights = scoring_weights or {
        "composite": DEFAULT_COMPOSITE_WEIGHTS,
        "heatmap": DEFAULT_HEATMAP_WEIGHTS,
    }
    composite_weights = weights["composite"]
    heatmap_weights = weights["heatmap"]
    co2_score = normalize_score(result.total_co2_ton_per_year, 0, 1_000_000)
    methanol_score = normalize_score(result.methanol_ton_per_year, 0, 300_000)
    market_score = _market_access_score(site_readiness)
    land_score = _land_score(site_readiness)
    utility_score = _utility_score(site_readiness)
    carbon_score = _carbon_credit_score(financial_assumption)
    strategic_score = _strategic_value_score(plant)
    h2_score = _h2_strategy_score(hydrogen_strategy)
    economic_return_score = normalize_score(result.irr, 0.05, 0.20)
    data_completeness_score = _data_completeness_score(
        plant,
        result,
        site_readiness,
        hydrogen_strategy,
        financial_assumption,
    )
    emission_quality_score = _emission_quality_score(emission_tests)
    permit_logistic_score = _permit_logistic_score(site_readiness, market_score)

    opportunity_score_value = round(
        (0.30 * co2_score)
        + (0.20 * methanol_score)
        + (0.15 * market_score)
        + (0.10 * land_score)
        + (0.10 * utility_score)
        + (0.05 * carbon_score)
        + (0.10 * strategic_score),
        4,
    )
    readiness_score_value = round(
        (0.20 * data_completeness_score)
        + (0.20 * emission_quality_score)
        + (0.15 * land_score)
        + (0.15 * utility_score)
        + (0.15 * h2_score)
        + (0.15 * permit_logistic_score),
        4,
    )

    confidence_inputs = [
        confidence_score_for_status(plant.data_status),
        confidence_score_for_status(scenario.data_status),
        confidence_score_for_status(financial_assumption.data_status if financial_assumption else "unknown"),
        confidence_score_for_status(site_readiness.data_status if site_readiness else "unknown"),
        confidence_score_for_status(hydrogen_strategy.data_status if hydrogen_strategy else "unknown"),
        *[confidence_score_for_status(test.data_status) for test in emission_tests],
    ]
    confidence_score_value = _safe_average(confidence_inputs)

    composite_score_value = round(
        (composite_weights["opportunity"] * opportunity_score_value)
        + (composite_weights["readiness"] * readiness_score_value)
        + (composite_weights["confidence"] * confidence_score_value),
        4,
    )
    heatmap_weight = round(
        max(
            0.0,
            min(
                1.0,
                (heatmap_weights["opportunity"] * opportunity_score_value)
                + (heatmap_weights["readiness"] * readiness_score_value)
                + (heatmap_weights["economic_return"] * economic_return_score)
                + (heatmap_weights["confidence"] * confidence_score_value),
            ),
        ),
        4,
    )

    component_scores = {
        "co2_availability_score": co2_score,
        "methanol_potential_score": methanol_score,
        "market_access_score": market_score,
        "land_availability_score": land_score,
        "utility_advantage_score": utility_score,
        "carbon_credit_potential_score": carbon_score,
        "strategic_value_score": strategic_score,
        "economic_return_score": economic_return_score,
        "data_completeness_score": data_completeness_score,
        "emission_data_quality_score": emission_quality_score,
        "land_readiness_score": land_score,
        "utility_readiness_score": utility_score,
        "h2_strategy_clarity_score": h2_score,
        "permit_logistic_readiness_score": permit_logistic_score,
    }
    data_gaps = derive_data_gaps(plant, result, site_readiness, hydrogen_strategy, financial_assumption)
    key_bottleneck = derive_key_bottleneck(data_gaps, component_scores)

    return {
        "opportunity_score": opportunity_score_value,
        "readiness_score": readiness_score_value,
        "confidence_score": confidence_score_value,
        "composite_score": composite_score_value,
        "co2_availability_score": co2_score,
        "methanol_potential_score": methanol_score,
        "h2_readiness_score": h2_score,
        "economic_return_score": economic_return_score,
        "infrastructure_score": utility_score,
        "land_port_score": round((land_score + market_score) / 2, 4),
        "market_access_score": market_score,
        "risk_permit_score": permit_logistic_score,
        "data_completeness_score": data_completeness_score,
        "emission_data_quality_score": emission_quality_score,
        "land_readiness_score": land_score,
        "utility_readiness_score": utility_score,
        "h2_strategy_clarity_score": h2_score,
        "permit_logistic_readiness_score": permit_logistic_score,
        "carbon_credit_potential_score": carbon_score,
        "strategic_value_score": strategic_score,
        "utility_advantage_score": utility_score,
        "component_scores": {
            **component_scores,
            "heatmap_weight": heatmap_weight,
            "data_gaps": data_gaps,
            "confidence_label": confidence_label(confidence_score_value),
            "opportunity_level": opportunity_level(opportunity_score_value),
            "composite_weights": composite_weights,
            "heatmap_weights": heatmap_weights,
        },
        "data_gap_count": len(data_gaps),
        "recommended_scheme": format_recommended_scheme(scenario.scheme),
        "key_bottleneck": key_bottleneck,
        "scoring_version": SCORING_VERSION,
    }


def latest_scenario_result(db: Session, scenario_id: str) -> ScenarioResult | None:
    return db.scalar(
        select(ScenarioResult)
        .where(ScenarioResult.scenario_id == scenario_id)
        .order_by(ScenarioResult.created_at.desc(), ScenarioResult.id.desc())
    )


def _load_scoring_inputs(
    db: Session,
    scenario: BusinessScenario,
    result: ScenarioResult,
) -> tuple[Plant, list[EmissionTest], SiteReadiness | None, HydrogenStrategy | None, FinancialAssumption | None]:
    plant = db.get(Plant, scenario.plant_id)
    if plant is None:
        raise ScoringInputError("Plant not found for scenario")
    emission_tests = list(db.scalars(select(EmissionTest).where(EmissionTest.plant_id == plant.id)))
    site_readiness = db.scalar(select(SiteReadiness).where(SiteReadiness.plant_id == plant.id))
    hydrogen_strategy = db.scalar(select(HydrogenStrategy).where(HydrogenStrategy.plant_id == plant.id))
    financial_assumption = db.scalar(
        select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id)
    )
    return plant, emission_tests, site_readiness, hydrogen_strategy, financial_assumption


def recalculate_unit_scoring(
    db: Session,
    *,
    scenario_id: str | None = None,
    scheme: str | None = None,
) -> tuple[str | None, list[UnitScoringResult]]:
    query = select(BusinessScenario)
    if scenario_id:
        query = query.where(BusinessScenario.id == scenario_id)
    if scheme and scheme != "all":
        query = query.where(BusinessScenario.scheme == scheme)
    scenarios = list(db.scalars(query.order_by(BusinessScenario.created_at, BusinessScenario.id)))
    if scenario_id and not scenarios:
        raise ScoringInputError("Scenario not found")

    scoring_run_id = str(uuid.uuid4())
    scoring_weights = load_scoring_weights(db)
    records: list[UnitScoringResult] = []
    for scenario in scenarios:
        result = latest_scenario_result(db, scenario.id)
        if result is None:
            continue
        plant, emission_tests, site_readiness, hydrogen_strategy, financial_assumption = _load_scoring_inputs(
            db,
            scenario,
            result,
        )
        score_data = calculate_unit_scores(
            plant,
            scenario,
            result,
            emission_tests,
            site_readiness,
            hydrogen_strategy,
            financial_assumption,
            scoring_weights,
        )
        record = UnitScoringResult(
            plant_id=plant.id,
            scenario_id=scenario.id,
            scenario_result_id=result.id,
            scoring_run_id=scoring_run_id,
            **score_data,
        )
        db.add(record)
        records.append(record)

    if not records:
        db.commit()
        return None, []

    for rank, record in enumerate(sorted(records, key=lambda item: item.composite_score, reverse=True), start=1):
        record.rank_position = rank

    db.commit()
    for record in records:
        db.refresh(record)
    return scoring_run_id, sorted(records, key=lambda item: item.rank_position or 999999)


def latest_scoring_records(
    db: Session,
    *,
    scenario_id: str | None = None,
    scheme: str | None = None,
    region: str | None = None,
    fuel_type: str | None = None,
    confidence: str | None = None,
    opportunity_filter: str | None = None,
) -> list[UnitScoringResult]:
    query = (
        select(UnitScoringResult, Plant, BusinessScenario)
        .join(UnitScoringResult.plant)
        .join(UnitScoringResult.scenario)
    )
    if scenario_id:
        query = query.where(UnitScoringResult.scenario_id == scenario_id)
    if scheme and scheme != "all":
        query = query.where(BusinessScenario.scheme == scheme)
    if region and region != "all":
        query = query.where(Plant.province == region)
    if fuel_type and fuel_type != "all":
        query = query.where(Plant.fuel_type == fuel_type)

    candidates: dict[tuple[str, str], UnitScoringResult] = {}
    for scoring, plant, scenario in db.execute(query):
        if confidence and confidence != "all":
            label = confidence_label(scoring.confidence_score).lower()
            if label != confidence.lower():
                continue
        if opportunity_filter and opportunity_filter != "all":
            level = opportunity_level(scoring.opportunity_score)
            if level != opportunity_filter.lower():
                continue

        key = (scoring.plant_id, scoring.scenario_id)
        current = candidates.get(key)
        if current is None or (scoring.created_at, scoring.id) > (current.created_at, current.id):
            candidates[key] = scoring

    records = sorted(candidates.values(), key=lambda item: item.composite_score, reverse=True)
    for rank, record in enumerate(records, start=1):
        record.rank_position = rank
    return records


def ranking_row_from_record(record: UnitScoringResult) -> dict[str, Any]:
    plant = record.plant
    scenario = record.scenario
    result = record.scenario_result
    heatmap_weight = float(record.component_scores.get("heatmap_weight", record.composite_score))
    return {
        "rank": record.rank_position or 0,
        "plant_id": plant.id,
        "site_id": plant.id,
        "scenario_id": scenario.id,
        "scenario_result_id": result.id,
        "scoring_result_id": record.id,
        "scenario_name": scenario.scenario_name,
        "scheme": scenario.scheme,
        "site_name": plant.plant_name,
        "unit_name": plant.unit_name,
        "province": plant.province,
        "city": plant.city,
        "latitude": plant.latitude,
        "longitude": plant.longitude,
        "capacity_mw": plant.capacity_mw,
        "fuel_type": plant.fuel_type,
        "composite_score": record.composite_score,
        "opportunity_score": record.opportunity_score,
        "readiness_score": record.readiness_score,
        "confidence_score": record.confidence_score,
        "heatmap_weight": heatmap_weight,
        "co2_tpy": result.total_co2_ton_per_year,
        "captured_co2_tpy": result.captured_co2_ton_per_year,
        "methanol_tpy": result.methanol_ton_per_year,
        "h2_required_tpy": result.h2_required_ton_per_year,
        "electrolyzer_required_mw": result.electrolyzer_required_mw,
        "gross_revenue_usd_per_year": result.gross_revenue_usd_per_year,
        "estimated_irr": result.irr,
        "estimated_lcom_usd_ton": result.lcom_usd_per_ton,
        "recommended_scheme": record.recommended_scheme,
        "key_bottleneck": record.key_bottleneck,
        "data_gap_count": record.data_gap_count,
        "data_confidence_label": confidence_label(record.confidence_score),
        "opportunity_level": opportunity_level(record.opportunity_score),
        "calculation_version": result.calculation_version,
    }

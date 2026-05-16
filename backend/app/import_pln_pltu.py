from __future__ import annotations

import json
import math
import re
import urllib.request
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.database import SessionLocal
from app.models import (
    BusinessScenario,
    EmissionTest,
    FinancialAssumption,
    HydrogenStrategy,
    Plant,
    SiteReadiness,
)
from app.services.calculations.co2 import calculate_emission_test_co2_ton_year
from app.services.scenario_simulation import SimulationInputError, run_scenario_simulation
from app.services.scoring import ScoringInputError, recalculate_unit_scoring
from app.services.settings import seed_default_settings


GCPT_GEOJSON_URL = "https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/interim_maps/gcpt_map_2026-01.geojson"
SCENARIO_NAME = "WIZ Align Public PLTU Screening"
EMISSION_STACK_ID = "Public benchmark CO2 estimate"
CAPACITY_FACTOR = 0.80
OPERATING_DAYS_PER_YEAR = 330
COAL_EMISSION_FACTOR_TCO2_PER_MWH = 0.95
CAPTURE_RATE = 0.85
PROCESS_EFFICIENCY = 0.60

PLN_TOKENS = (
    "pln",
    "pt indonesia power",
    "pln indonesia power",
    "pln nusantara power",
    "pt pln nusantara power",
    "pembangkitan jawa bali",
    "pjb",
)

FINANCIAL_BENCHMARK = {
    "methanol_price_usd_per_ton": 1250,
    "grey_methanol_price_usd_per_ton": 350,
    "hydrogen_price_usd_per_kg": 3.0,
    "electricity_price_usd_per_kwh": 0.06,
    "carbon_credit_price_idr_per_ton": 58800,
    "exchange_rate_idr_usd": 17500,
    "discount_rate": 0.10,
    "tax_rate": 0.22,
    "opex_percent_capex": 0.04,
    "data_status": "benchmark",
    "confidence_level": "low",
}


@dataclass(frozen=True)
class ImportRow:
    plant_name: str
    unit_name: str
    province: str | None
    latitude: float | None
    longitude: float | None
    capacity_mw: float
    owner: str
    status: str
    source_url: str | None
    pln_ownership_percent: float | None


def _clean_text(value: object, max_length: int | None = None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text[:max_length] if max_length else text


def _clean_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _pln_related(properties: dict[str, Any]) -> bool:
    haystack = " ".join(
        str(properties.get(field) or "")
        for field in ("owner", "parent", "owner-search", "parent-search", "name")
    ).lower()
    return any(token in haystack for token in PLN_TOKENS)


def _pln_ownership_percent(owner: str, parent: str) -> float | None:
    text = f"{owner}; {parent}"
    matches = re.findall(r"PLN[^;\[]*(?:\[(\d+(?:\.\d+)?)%\])?", text, flags=re.IGNORECASE)
    percentages = [float(match) for match in matches if match]
    if percentages:
        return max(percentages)
    return 100.0 if "pln" in text.lower() else None


def _load_rows() -> tuple[list[ImportRow], int, int]:
    with urllib.request.urlopen(GCPT_GEOJSON_URL, timeout=60) as response:
        geojson = json.loads(response.read().decode("utf-8"))

    indonesia_total = 0
    operating_total = 0
    rows: list[ImportRow] = []
    for feature in geojson.get("features", []):
        properties = feature.get("properties") or {}
        if properties.get("country-area1") != "Indonesia":
            continue
        indonesia_total += 1
        if properties.get("status") != "operating":
            continue
        operating_total += 1
        if not _pln_related(properties):
            continue

        capacity_mw = _clean_float(properties.get("capacity"))
        latitude = _clean_float(properties.get("Latitude"))
        longitude = _clean_float(properties.get("Longitude"))
        plant_name = _clean_text(properties.get("name"), 160)
        if plant_name is None or capacity_mw is None or latitude is None or longitude is None:
            continue

        owner = _clean_text(properties.get("owner"), 160) or _clean_text(properties.get("parent"), 160) or "PLN-related"
        parent = _clean_text(properties.get("parent")) or ""
        rows.append(
            ImportRow(
                plant_name=plant_name,
                unit_name=_clean_text(properties.get("unit-name"), 120) or "Unit aggregate",
                province=_clean_text(properties.get("subnational"), 120),
                latitude=latitude,
                longitude=longitude,
                capacity_mw=capacity_mw,
                owner=owner,
                status="operating",
                source_url=_clean_text(properties.get("url")),
                pln_ownership_percent=_pln_ownership_percent(owner, parent),
            )
        )
    return rows, indonesia_total, operating_total


def _upsert_record(db: Session, model: type, lookup: dict[str, Any], values: dict[str, Any]) -> Any:
    query = select(model)
    for field, value in lookup.items():
        query = query.where(getattr(model, field) == value)
    record = db.scalar(query)
    if record is None:
        record = model(**lookup, **values)
        db.add(record)
    else:
        for field, value in values.items():
            setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def _target_co2_tpy(capacity_mw: float) -> float:
    return capacity_mw * CAPACITY_FACTOR * 8760 * COAL_EMISSION_FACTOR_TCO2_PER_MWH


def _benchmark_stack_diameter(capacity_mw: float) -> float:
    base_row = {
        "stack_diameter_m": 1.0,
        "gas_velocity_m_s": 18.0,
        "flue_gas_temperature_c": 120.0,
        "co2_percent_dry": 12.0,
        "moisture_percent": 8.0,
    }
    base_co2 = calculate_emission_test_co2_ton_year(base_row, OPERATING_DAYS_PER_YEAR) or 1.0
    return round(max(1.0, math.sqrt(_target_co2_tpy(capacity_mw) / base_co2)), 3)


def _capex_assumptions(capacity_mw: float) -> dict[str, float]:
    target_co2 = _target_co2_tpy(capacity_mw)
    captured_co2 = target_co2 * CAPTURE_RATE
    methanol_tpy = captured_co2 * (32.04 / 44.01) * PROCESS_EFFICIENCY
    h2_tpy = methanol_tpy * (6.048 / 32.04)
    electrolyzer_mw = h2_tpy * 1000 * 50 / (OPERATING_DAYS_PER_YEAR * 24)
    return {
        "capex_capture_usd": round(captured_co2 * 450),
        "capex_electrolyzer_usd": round(electrolyzer_mw * 700_000),
        "capex_methanol_plant_usd": round(methanol_tpy * 600),
        "capex_storage_port_usd": round(max(10_000_000, capacity_mw * 75_000)),
    }


def _upsert_public_screening_inputs(db: Session, row: ImportRow) -> tuple[Plant, BusinessScenario]:
    plant = _upsert_record(
        db,
        Plant,
        {"plant_name": row.plant_name, "unit_name": row.unit_name},
        {
            "province": row.province,
            "city": None,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "capacity_mw": row.capacity_mw,
            "fuel_type": "coal",
            "status": row.status,
            "capacity_factor": CAPACITY_FACTOR,
            "operating_days_per_year": OPERATING_DAYS_PER_YEAR,
            "owner": row.owner,
            "data_status": "estimated",
            "confidence_level": "medium",
        },
    )

    _upsert_record(
        db,
        EmissionTest,
        {"plant_id": plant.id, "stack_id": EMISSION_STACK_ID},
        {
            "test_date": None,
            "lab_name": "GEM GCPT public screening benchmark",
            "stack_diameter_m": _benchmark_stack_diameter(row.capacity_mw),
            "gas_velocity_m_s": 18.0,
            "flue_gas_temperature_c": 120.0,
            "co2_percent_dry": 12.0,
            "o2_percent": 8.0,
            "moisture_percent": 8.0,
            "so2_mg_nm3": None,
            "nox_mg_nm3": None,
            "particulate_mg_nm3": None,
            "hg_mg_nm3": None,
            "compliance_status": row.source_url,
            "data_status": "benchmark",
            "confidence_level": "low",
        },
    )

    _upsert_record(
        db,
        SiteReadiness,
        {"plant_id": plant.id},
        {
            "available_land_ha": round(max(2.0, min(30.0, row.capacity_mw / 80)), 2),
            "land_status": "Existing operating PLTU site - public screening assumption",
            "distance_to_stack_km": 0.5,
            "has_port_or_jetty": None,
            "distance_to_port_km": None,
            "port_capacity_dwt": None,
            "road_access": "Existing plant access assumed",
            "water_availability": "Existing plant water system assumed",
            "power_availability": "Existing grid connection assumed",
            "utility_readiness": "Existing plant utilities assumed",
            "permit_risk": "medium",
            "social_risk": "unknown",
            "data_status": "benchmark",
            "confidence_level": "low",
        },
    )

    _upsert_record(
        db,
        HydrogenStrategy,
        {"plant_id": plant.id},
        {
            "existing_h2_available": False,
            "h2_strategy": "Dedicated electrolysis or imported green H2 to be confirmed",
            "h2_cost_case": "public screening benchmark",
            "h2_cost_usd_per_kg": FINANCIAL_BENCHMARK["hydrogen_price_usd_per_kg"],
            "h2_readiness_score": 0.35,
            "data_status": "benchmark",
            "confidence_level": "low",
        },
    )

    scenario = _upsert_record(
        db,
        BusinessScenario,
        {"plant_id": plant.id, "scenario_name": SCENARIO_NAME},
        {
            "scheme": "align",
            "pln_ownership_percent": row.pln_ownership_percent,
            "partner_capex_responsibility_percent": 100,
            "pln_capex_responsibility_percent": 0,
            "revenue_model": "public_screening_partner_capex",
            "capture_rate": CAPTURE_RATE,
            "process_efficiency": PROCESS_EFFICIENCY,
            "data_status": "benchmark",
            "confidence_level": "low",
        },
    )

    _upsert_record(
        db,
        FinancialAssumption,
        {"scenario_id": scenario.id},
        {**FINANCIAL_BENCHMARK, **_capex_assumptions(row.capacity_mw)},
    )
    return plant, scenario


def import_public_screening() -> dict[str, Any]:
    rows, indonesia_total, operating_total = _load_rows()
    with SessionLocal() as db:
        seed_default_settings(db)
        scenario_ids: list[str] = []
        plant_ids: list[str] = []
        failed_simulations: list[str] = []

        for row in rows:
            plant, scenario = _upsert_public_screening_inputs(db, row)
            plant_ids.append(plant.id)
            scenario_ids.append(scenario.id)
            try:
                run_scenario_simulation(db, scenario.id)
            except (SimulationInputError, ValueError) as exc:
                failed_simulations.append(f"{row.plant_name} {row.unit_name}: {exc}")

        try:
            scoring_run_id, scoring_records = recalculate_unit_scoring(db, scheme="align")
        except ScoringInputError:
            scoring_run_id, scoring_records = None, []

    return {
        "source_url": GCPT_GEOJSON_URL,
        "indonesia_coal_units_in_source": indonesia_total,
        "indonesia_operating_coal_units_in_source": operating_total,
        "pln_related_operating_units_imported": len(rows),
        "plants_touched": len(set(plant_ids)),
        "scenarios_touched": len(set(scenario_ids)),
        "failed_simulations": failed_simulations,
        "scoring_run_id": scoring_run_id,
        "scoring_records_created": len(scoring_records),
    }


def main() -> None:
    result = import_public_screening()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

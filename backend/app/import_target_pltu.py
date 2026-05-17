from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.database import SessionLocal
from app.models import (
    BusinessScenario,
    DataGap,
    Document,
    EmissionTest,
    FinancialAssumption,
    HydrogenStrategy,
    LlmInsight,
    Plant,
    PreFeedCostBasisSelection,
    PreFeedCostItem,
    PreFeedDecisionGate,
    PreFeedMrvAssumption,
    PreFeedOfftakeProspect,
    PreFeedPackage,
    PreFeedPackageDocument,
    PreFeedPriceDeck,
    PreFeedRisk,
    PreFeedVendorProposal,
    ScenarioResult,
    SensitivityResult,
    SiteReadiness,
    UnitScoringResult,
)
from app.services.calculations.co2 import calculate_emission_test_co2_ton_year
from app.services.scenario_simulation import SimulationInputError, run_scenario_simulation
from app.services.scoring import ScoringInputError, recalculate_unit_scoring
from app.services.settings import seed_default_settings


SCENARIO_NAME = "WIZ Align Curated PLTU Screening"
UNIT_NAME = "Site aggregate"
EMISSION_STACK_ID = "Regulatory BME + public CO2 benchmark"
CAPACITY_FACTOR = 0.80
OPERATING_DAYS_PER_YEAR = 330
COAL_EMISSION_FACTOR_TCO2_PER_MWH = 0.95
CAPTURE_RATE = 0.85
PROCESS_EFFICIENCY = 0.60

BME_EXISTING_COAL = {
    "so2_mg_nm3": 550.0,
    "nox_mg_nm3": 550.0,
    "particulate_mg_nm3": 100.0,
    "hg_mg_nm3": 0.03,
}

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
class TargetPltuSite:
    plant_name: str
    capacity_mw: float
    province: str
    city: str
    latitude: float
    longitude: float
    owner: str
    source_label: str
    source_url: str
    note: str
    confidence_level: str = "medium"
    data_status: str = "estimated"


TARGET_PLTU_SITES: tuple[TargetPltuSite, ...] = (
    TargetPltuSite(
        "UP Tenayan",
        220,
        "Riau",
        "Pekanbaru",
        0.56437,
        101.52345,
        "PT PLN (Persero)",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Pekanbaru_Tenayan_power_station",
        "PLTU 2 x 110 MW.",
        "high",
    ),
    TargetPltuSite(
        "UP Indramayu",
        990,
        "Jawa Barat",
        "Indramayu",
        -6.274738,
        107.97043,
        "PT PLN (Persero)",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Indramayu_power_station",
        "PLTU 3 x 330 MW; cancelled expansions excluded.",
        "high",
    ),
    TargetPltuSite(
        "UP Rembang",
        630,
        "Jawa Tengah",
        "Rembang",
        -6.636,
        111.4749,
        "PT PLN (Persero)",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Rembang_power_station",
        "PLTU 2 x 315 MW.",
        "high",
    ),
    TargetPltuSite(
        "UP Tanjung Awar-Awar",
        700,
        "Jawa Timur",
        "Tuban",
        -6.810524,
        111.995503,
        "PT PLN (Persero)",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Tanjung_Awar-Awar_power_station",
        "PLTU 2 x 350 MW.",
        "high",
    ),
    TargetPltuSite(
        "UP Pacitan",
        630,
        "Jawa Timur",
        "Pacitan",
        -8.257818,
        111.373558,
        "PT PLN (Persero)",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Pacitan_power_station",
        "PLTU 2 x 315 MW.",
        "high",
    ),
    TargetPltuSite(
        "UP Paiton",
        1460,
        "Jawa Timur",
        "Probolinggo",
        -7.713041,
        113.578536,
        "PT PLN (Persero)",
        "GEM GCPT weighted centroid from PLN Paiton 1-2 and Paiton 9",
        "https://www.gem.wiki/PLN_Paiton_power_station",
        "Paiton 1-2 plus Paiton 9; coordinate is a capacity-weighted site centroid.",
        "medium",
    ),
    TargetPltuSite(
        "UP Kaltim Teluk / Teluk Balikpapan",
        220,
        "Kalimantan Timur",
        "Balikpapan",
        -1.17036,
        116.78872,
        "PT PLN (Persero)",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Kaltim_Teluk_Balikpapan_power_station",
        "PLTU 2 x 110 MW; cancelled expansion excluded.",
        "high",
    ),
    TargetPltuSite(
        "UP Pulang Pisau",
        120,
        "Kalimantan Tengah",
        "Pulang Pisau",
        -2.822646,
        114.208831,
        "PT PLN (Persero)",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Kalteng-1_Pulang_Pisau_power_station",
        "PLTU 2 x 60 MW.",
        "high",
    ),
    TargetPltuSite(
        "UP Nagan Raya",
        220,
        "Aceh",
        "Nagan Raya",
        4.1075504,
        96.1988906,
        "PT PLN (Persero)",
        "GEM GCPT exact unit 1-2 coordinates",
        "https://www.gem.wiki/Nagan_Raya_power_station",
        "Uses the 2 x 110 MW unit-1/2 coordinate; newer 2 x 225 MW units excluded.",
        "high",
    ),
    TargetPltuSite(
        "UP Bukit Asam",
        260,
        "Sumatera Selatan",
        "Muara Enim",
        -3.73213,
        103.797527,
        "PT PLN (Persero)",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Bukit_Asam_Muara_Enim_power_station",
        "PLTU batubara 4 x 65 MW.",
        "high",
    ),
    TargetPltuSite(
        "UP Sebalang",
        200,
        "Lampung",
        "Lampung Selatan",
        -5.58594,
        105.38719,
        "PT PLN (Persero)",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Lampung_Sebalang_power_station",
        "Uses PLTU 2 x 100 MW; public 221.5 MW references need internal reconciliation.",
        "medium",
    ),
    TargetPltuSite(
        "UP Tarahan",
        200,
        "Lampung",
        "Lampung Selatan",
        -5.521207,
        105.353477,
        "PT PLN (Persero)",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Tarahan_power_station",
        "Uses unit 3-4, PLTU 2 x 100 MW.",
        "high",
    ),
    TargetPltuSite(
        "UP Punagaya",
        220,
        "Sulawesi Selatan",
        "Jeneponto",
        -5.623635,
        119.550822,
        "PT PLN (Persero)",
        "GEM GCPT exact Takalar/Punagaya coordinate plus PLN UP Punagaya capacity page",
        "https://www.gem.wiki/Takalar_power_station",
        "Public sources show 2 x 100 MW or 2 x 110 MW gross; seeded with user target 220 MW.",
        "medium",
    ),
    TargetPltuSite(
        "PLTU Tembilahan",
        14,
        "Riau",
        "Indragiri Hilir",
        -0.2989716,
        103.2048053,
        "PLN group / PLN NP Services O&M",
        "OpenStreetMap/Nominatim named plant coordinate",
        "https://www.openstreetmap.org/search?query=PLTU%20Tembilahan",
        "PLTU 2 x 7 MW.",
        "high",
    ),
    TargetPltuSite(
        "PLTU Ketapang",
        20,
        "Kalimantan Barat",
        "Ketapang",
        -1.780572,
        109.942072,
        "PLN group / PLN NP Services O&M",
        "Ketapang environmental office TPS LB3 coordinate, longitude corrected to West Kalimantan",
        "https://lhketapang.wixsite.com/lhketapang/post/2017/11/17/izin-penyimpanan-sementara-limbah-b3-pltu-ketapang",
        "PLTU 2 x 10 MW; official local post appears to mistype longitude as 119E.",
        "medium",
    ),
    TargetPltuSite(
        "PLTU Kendari 1-2 / Nii Tanasa",
        24,
        "Sulawesi Tenggara",
        "Konawe",
        -3.895295,
        122.537864,
        "PLN group / PLN NP Services O&M",
        "OpenStreetMap plant polygon centroid and PLN public Nii Tanasa references",
        "https://www.openstreetmap.org/way/943189957",
        "User target 24 MW for Kendari 1-2; public sources describe Nii Tanasa as 2 x 10 MW or 3 x 10 MW.",
        "medium",
    ),
    TargetPltuSite(
        "PLTU Amurang",
        50,
        "Sulawesi Utara",
        "Minahasa Selatan",
        1.182502,
        124.480564,
        "PLN group / PLN NP Services O&M",
        "GEM GCPT Amurang coordinate",
        "https://www.gem.wiki/Amurang_power_station",
        "User target 50 MW; GEM public rows show 2 x 30 MW for Amurang station.",
        "medium",
    ),
    TargetPltuSite(
        "PLTU Anggrek",
        55,
        "Gorontalo",
        "Gorontalo Utara",
        0.850288,
        122.796453,
        "PLN group / PLN NP Services O&M",
        "Cybo/Google Plus Code geocode for PLTU Anggrek",
        "https://bukutelepon.cybo.com/ID-biz/pltu-anggrek",
        "Public address is Ilangata, Anggrek; coordinate decoded from plus code VQ2W+4H8.",
        "medium",
    ),
    TargetPltuSite(
        "PLTU Ampana",
        7,
        "Sulawesi Tengah",
        "Tojo Una-Una",
        -1.0985,
        121.8114,
        "PLN group / PLN NP Services O&M",
        "Sabo village public geocode plus PLN/PLN NP Services address references",
        "https://kodepos.co.id/kodepos/sulawesi-tengah/kabupaten-tojo-una-una/ampana-tete/sabo",
        "Plant is publicly described at Desa Sabo; no public fence-line coordinate was found.",
        "low",
    ),
    TargetPltuSite(
        "PLTU Bolok",
        33,
        "Nusa Tenggara Timur",
        "Kupang",
        -10.240166,
        123.49135,
        "PLN group / PLN NP Services O&M",
        "OpenStreetMap/Nominatim named plant coordinate",
        "https://www.openstreetmap.org/way/611789533",
        "Unit jasa O&M; public capacity references commonly show 2 x 16.5 MW.",
        "high",
    ),
    TargetPltuSite(
        "PLTU Ropa",
        14,
        "Nusa Tenggara Timur",
        "Ende",
        -8.509167,
        121.700556,
        "PLN group / PLN NP Services O&M",
        "Wikimapia/Cybo public map coordinate converted from DMS",
        "https://wikimapia.org/25361683/id/Pembangkit-Listrik-Tenaga-Uap-Ropa",
        "Unit jasa O&M; public references show 2 x 7 MW at Ropa/Keliwumbu.",
        "medium",
    ),
    TargetPltuSite(
        "PLTU Tidore",
        14,
        "Maluku Utara",
        "Tidore Kepulauan",
        0.7398516,
        127.3877213,
        "PLN group / PLN NP Services O&M",
        "OpenStreetMap/Nominatim named plant coordinate",
        "https://www.openstreetmap.org/search?query=PLTU%20Tidore",
        "Unit jasa O&M.",
        "high",
    ),
    TargetPltuSite(
        "PLTU Kendari #3",
        9.8,
        "Sulawesi Tenggara",
        "Konawe",
        -3.895295,
        122.537864,
        "PLN group / PLN NP Services O&M",
        "OpenStreetMap plant polygon centroid and PLN public Nii Tanasa unit-3 references",
        "https://www.openstreetmap.org/way/943189957",
        "Unit jasa O&M; public sources refer to 1 x 10 MW unit 3.",
        "medium",
    ),
    TargetPltuSite(
        "PLTU Bangka / Air Anyir",
        60,
        "Kepulauan Bangka Belitung",
        "Bangka",
        -2.079245,
        106.149617,
        "PLN group / PLN NP Services O&M",
        "GEM GCPT exact project and unit coordinates",
        "https://www.gem.wiki/Bangka_Baru_power_station",
        "Unit jasa O&M; 2 x 30 MW.",
        "high",
    ),
    TargetPltuSite(
        "PLTU Belitung / Suge",
        33,
        "Kepulauan Bangka Belitung",
        "Belitung",
        -2.8932592,
        107.5638809,
        "PLN group / PLN NP Services O&M",
        "OpenStreetMap/Nominatim named plant coordinate plus PLN NP Services page",
        "https://www.pln-npservices.com/bio-diversity/pltu-belitung/",
        "PLN NP Services states Suge Belitung 2 x 16.5 MW.",
        "high",
    ),
    TargetPltuSite(
        "PLTU Sambelia",
        100,
        "Nusa Tenggara Barat",
        "Lombok Timur",
        -8.4221991,
        116.7110024,
        "PLN group / PLN NP Services O&M",
        "OpenStreetMap/Nominatim named plant coordinate and PLN NP O&M references",
        "https://www.openstreetmap.org/search?query=PLTU%20Sambelia",
        "Unit jasa O&M; latest O&M/ownership status should still be confirmed internally.",
        "medium",
    ),
)


def _count_rows(db: Session, model: type) -> int:
    return int(db.scalar(select(func.count()).select_from(model)) or 0)


def _clear_existing_dataset(db: Session) -> dict[str, int]:
    deleted: dict[str, int] = {}
    db.execute(update(Document).values(plant_id=None, scenario_id=None))
    db.execute(update(LlmInsight).values(plant_id=None, scenario_id=None))

    delete_order = (
        PreFeedDecisionGate,
        PreFeedRisk,
        PreFeedCostBasisSelection,
        PreFeedCostItem,
        PreFeedVendorProposal,
        PreFeedMrvAssumption,
        PreFeedOfftakeProspect,
        PreFeedPriceDeck,
        PreFeedPackageDocument,
        PreFeedPackage,
        SensitivityResult,
        UnitScoringResult,
        ScenarioResult,
        DataGap,
        FinancialAssumption,
        EmissionTest,
        SiteReadiness,
        HydrogenStrategy,
        BusinessScenario,
        Plant,
    )
    for model in delete_order:
        deleted[model.__tablename__] = _count_rows(db, model)
        db.execute(delete(model))
    db.commit()
    return deleted


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
    h2_tpy = methanol_tpy * (6.048 / 32.04) / 0.90
    electrolyzer_mw = (h2_tpy * 1000 / OPERATING_DAYS_PER_YEAR) / 480
    return {
        "capex_capture_usd": round(captured_co2 * 450),
        "capex_electrolyzer_usd": round(electrolyzer_mw * 700_000),
        "capex_methanol_plant_usd": round(methanol_tpy * 600),
        "capex_storage_port_usd": round(max(10_000_000, capacity_mw * 75_000)),
    }


def _create_inputs(db: Session, site: TargetPltuSite) -> tuple[Plant, BusinessScenario]:
    plant = Plant(
        plant_name=site.plant_name,
        unit_name=UNIT_NAME,
        province=site.province,
        city=site.city,
        latitude=site.latitude,
        longitude=site.longitude,
        capacity_mw=site.capacity_mw,
        fuel_type="coal",
        status="operating",
        capacity_factor=CAPACITY_FACTOR,
        operating_days_per_year=OPERATING_DAYS_PER_YEAR,
        owner=site.owner,
        data_status=site.data_status,
        confidence_level=site.confidence_level,
    )
    db.add(plant)
    db.flush()

    db.add(
        EmissionTest(
            plant_id=plant.id,
            stack_id=EMISSION_STACK_ID,
            test_date=None,
            lab_name="Permen LHK P.15/2019 BME plus public CO2 benchmark",
            stack_diameter_m=_benchmark_stack_diameter(site.capacity_mw),
            gas_velocity_m_s=18.0,
            flue_gas_temperature_c=120.0,
            co2_percent_dry=12.0,
            o2_percent=8.0,
            moisture_percent=8.0,
            so2_mg_nm3=BME_EXISTING_COAL["so2_mg_nm3"],
            nox_mg_nm3=BME_EXISTING_COAL["nox_mg_nm3"],
            particulate_mg_nm3=BME_EXISTING_COAL["particulate_mg_nm3"],
            hg_mg_nm3=BME_EXISTING_COAL["hg_mg_nm3"],
            compliance_status="Permen LHK P.15/2019 existing-coal BME",
            data_status="benchmark",
            confidence_level="medium",
        )
    )
    db.add(
        SiteReadiness(
            plant_id=plant.id,
            available_land_ha=round(max(1.0, min(30.0, site.capacity_mw / 80)), 2),
            land_status="Existing PLTU footprint; land availability needs site confirmation",
            distance_to_stack_km=0.5,
            has_port_or_jetty=None,
            distance_to_port_km=None,
            port_capacity_dwt=None,
            road_access="Existing plant access assumed from public site operation",
            water_availability="Existing PLTU water system assumed",
            power_availability="Existing grid-connected PLTU",
            utility_readiness="Existing plant utilities assumed",
            permit_risk="medium",
            social_risk="unknown",
            data_status="benchmark",
            confidence_level="low",
        )
    )
    db.add(
        HydrogenStrategy(
            plant_id=plant.id,
            existing_h2_available=False,
            h2_strategy="Dedicated electrolysis or imported green H2 to be confirmed",
            h2_cost_case="public screening benchmark",
            h2_cost_usd_per_kg=FINANCIAL_BENCHMARK["hydrogen_price_usd_per_kg"],
            h2_readiness_score=0.35,
            data_status="benchmark",
            confidence_level="low",
        )
    )
    scenario = BusinessScenario(
        plant_id=plant.id,
        scenario_name=SCENARIO_NAME,
        scheme="align",
        pln_ownership_percent=100,
        partner_capex_responsibility_percent=100,
        pln_capex_responsibility_percent=0,
        revenue_model="curated_public_screening_partner_capex",
        capture_rate=CAPTURE_RATE,
        process_efficiency=PROCESS_EFFICIENCY,
        data_status="benchmark",
        confidence_level="low",
    )
    db.add(scenario)
    db.flush()
    db.add(
        FinancialAssumption(
            scenario_id=scenario.id,
            **FINANCIAL_BENCHMARK,
            **_capex_assumptions(site.capacity_mw),
        )
    )
    return plant, scenario


def import_curated_pltu_dataset(db: Session, *, clear_existing: bool = True) -> dict[str, Any]:
    if len({site.plant_name for site in TARGET_PLTU_SITES}) != len(TARGET_PLTU_SITES):
        raise ValueError("Curated PLTU target list contains duplicate plant names")

    seed_default_settings(db)
    deleted = _clear_existing_dataset(db) if clear_existing else {}
    scenario_ids: list[str] = []
    plant_ids: list[str] = []
    source_rows: list[dict[str, Any]] = []

    for site in TARGET_PLTU_SITES:
        plant, scenario = _create_inputs(db, site)
        plant_ids.append(plant.id)
        scenario_ids.append(scenario.id)
        source_rows.append(
            {
                "plant_name": site.plant_name,
                "capacity_mw": site.capacity_mw,
                "latitude": site.latitude,
                "longitude": site.longitude,
                "confidence_level": site.confidence_level,
                "source_label": site.source_label,
                "source_url": site.source_url,
                "note": site.note,
            }
        )
    db.commit()

    failed_simulations: list[str] = []
    for site, scenario_id in zip(TARGET_PLTU_SITES, scenario_ids, strict=True):
        try:
            run_scenario_simulation(db, scenario_id)
        except (SimulationInputError, ValueError) as exc:
            failed_simulations.append(f"{site.plant_name}: {exc}")

    try:
        scoring_run_id, scoring_records = recalculate_unit_scoring(db, scheme="align")
    except ScoringInputError:
        scoring_run_id, scoring_records = None, []

    return {
        "plants_deleted": deleted.get("plants", 0),
        "scenarios_deleted": deleted.get("business_scenarios", 0),
        "scoring_deleted": deleted.get("unit_scoring_results", 0),
        "target_sites": len(TARGET_PLTU_SITES),
        "plants_created": len(plant_ids),
        "scenarios_created": len(scenario_ids),
        "total_capacity_mw": round(sum(site.capacity_mw for site in TARGET_PLTU_SITES), 3),
        "failed_simulations": failed_simulations,
        "scoring_run_id": scoring_run_id,
        "scoring_records_created": len(scoring_records),
        "bme_existing_coal_mg_nm3": BME_EXISTING_COAL,
        "sources": source_rows,
    }


def import_curated_pltu_dataset_to_default_db() -> dict[str, Any]:
    with SessionLocal() as db:
        return import_curated_pltu_dataset(db, clear_existing=True)


def main() -> None:
    result = import_curated_pltu_dataset_to_default_db()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

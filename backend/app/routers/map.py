from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.scoring import GeoJSONFeatureCollection
from app.services.port_intelligence import (
    build_economic_zones_geojson,
    build_export_corridors_geojson,
    build_port_aware_unit_geojson,
    build_ports_geojson,
)
from app.services.scoring import latest_scoring_records


router = APIRouter(prefix="/map", tags=["map"])


@router.get("/unit-opportunity", response_model=GeoJSONFeatureCollection)
def read_unit_opportunity_geojson(
    scenario_id: str | None = None,
    scheme: str | None = None,
    region: str | None = None,
    fuel_type: str | None = None,
    confidence: str | None = Query(default=None, pattern="^(all|high|medium|low|unknown)$"),
    opportunity_level: str | None = Query(default=None, pattern="^(all|low|medium|high|priority)$"),
    db: Session = Depends(get_db),
) -> dict:
    records = latest_scoring_records(
        db,
        scenario_id=scenario_id,
        scheme=scheme,
        region=region,
        fuel_type=fuel_type,
        confidence=confidence,
        opportunity_filter=opportunity_level,
    )
    return build_port_aware_unit_geojson(records)


@router.get("/ports", response_model=GeoJSONFeatureCollection)
def read_ports_geojson() -> dict:
    return build_ports_geojson()


@router.get("/economic-zones", response_model=GeoJSONFeatureCollection)
def read_economic_zones_geojson(
    scenario_id: str | None = None,
    scheme: str | None = None,
    region: str | None = None,
    fuel_type: str | None = None,
    confidence: str | None = Query(default=None, pattern="^(all|high|medium|low|unknown)$"),
    opportunity_level: str | None = Query(default=None, pattern="^(all|low|medium|high|priority)$"),
    db: Session = Depends(get_db),
) -> dict:
    records = latest_scoring_records(
        db,
        scenario_id=scenario_id,
        scheme=scheme,
        region=region,
        fuel_type=fuel_type,
        confidence=confidence,
        opportunity_filter=opportunity_level,
    )
    return build_economic_zones_geojson(records)


@router.get("/export-corridors", response_model=GeoJSONFeatureCollection)
def read_export_corridors_geojson(
    scenario_id: str | None = None,
    scheme: str | None = None,
    region: str | None = None,
    fuel_type: str | None = None,
    confidence: str | None = Query(default=None, pattern="^(all|high|medium|low|unknown)$"),
    opportunity_level: str | None = Query(default=None, pattern="^(all|low|medium|high|priority)$"),
    db: Session = Depends(get_db),
) -> dict:
    records = latest_scoring_records(
        db,
        scenario_id=scenario_id,
        scheme=scheme,
        region=region,
        fuel_type=fuel_type,
        confidence=confidence,
        opportunity_filter=opportunity_level,
    )
    return build_export_corridors_geojson(records)

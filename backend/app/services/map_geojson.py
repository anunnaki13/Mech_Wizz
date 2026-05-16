from typing import Any

from app.models import UnitScoringResult
from app.services.scoring import ranking_row_from_record


def build_unit_opportunity_geojson(records: list[UnitScoringResult]) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    for record in records:
        row = ranking_row_from_record(record)
        longitude = row["longitude"]
        latitude = row["latitude"]
        if longitude is None or latitude is None:
            continue
        features.append(
            {
                "type": "Feature",
                "id": row["plant_id"],
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                },
                "properties": {
                    "site_id": row["site_id"],
                    "site_name": row["site_name"],
                    "unit_name": row["unit_name"],
                    "province": row["province"],
                    "city": row["city"],
                    "capacity_mw": row["capacity_mw"],
                    "fuel_type": row["fuel_type"],
                    "scenario_id": row["scenario_id"],
                    "scenario_name": row["scenario_name"],
                    "scheme": row["scheme"],
                    "opportunity_score": row["opportunity_score"],
                    "readiness_score": row["readiness_score"],
                    "confidence_score": row["confidence_score"],
                    "composite_score": row["composite_score"],
                    "co2_tpy": row["co2_tpy"],
                    "captured_co2_tpy": row["captured_co2_tpy"],
                    "methanol_tpy": row["methanol_tpy"],
                    "h2_required_tpy": row["h2_required_tpy"],
                    "estimated_irr": row["estimated_irr"],
                    "estimated_lcom_usd_ton": row["estimated_lcom_usd_ton"],
                    "rank_position": row["rank"],
                    "data_confidence_label": row["data_confidence_label"],
                    "heatmap_weight": row["heatmap_weight"],
                    "recommended_scheme": row["recommended_scheme"],
                    "key_bottleneck": row["key_bottleneck"],
                    "data_gap_count": row["data_gap_count"],
                    "opportunity_level": row["opportunity_level"],
                    "status": "pilot_candidate" if row["rank"] == 1 else "candidate",
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}

import json
import math
import re
import urllib.parse
import urllib.request
from functools import lru_cache
from typing import Any

from app.models import UnitScoringResult
from app.services.scoring import ranking_row_from_record


WPI_API_URL = "https://msi.nga.mil/api/publications/world-port-index"
WPI_SOURCE_URL = "https://msi.nga.mil/Publications/WPI"
SINGAPORE_METHANOL_REFERENCE_URL = (
    "https://www.mpa.gov.sg/media-centre/details/singapore-gears-up-to-meet-net-zero-needs-of-shipping"
)
SINGAPORE_TARGET_PORT = "Jurong Island"

_DMS_PATTERN = re.compile(r'^\s*(\d+(?:\.\d+)?)\D+(\d+(?:\.\d+)?)\D+(\d+(?:\.\d+)?)"?\s*([NSEW])', re.I)

FALLBACK_WPI_PORTS: dict[str, list[dict[str, Any]]] = {
    "Indonesia": [
        {
            "portNumber": 52790,
            "portName": "Banten",
            "countryCode": "ID",
            "countryName": "Indonesia",
            "harborSize": "V",
            "harborType": "OR",
            "xcoord": 105.966667,
            "ycoord": -6.016667,
            "chDepth": "14",
            "anDepth": "20",
            "loWharves": "Y",
            "loLiquidBulk": "Y",
            "firstPortOfEntry": "Y",
        },
        {
            "portNumber": 51560,
            "portName": "Tanjung Priok",
            "countryCode": "ID",
            "countryName": "Indonesia",
            "harborSize": "L",
            "harborType": "CN",
            "xcoord": 106.883333,
            "ycoord": -6.1,
            "chDepth": "12",
            "anDepth": "14",
            "loWharves": "Y",
            "loContainer": "Y",
            "firstPortOfEntry": "Y",
        },
        {
            "portNumber": 50290,
            "portName": "Tanjung Perak",
            "countryCode": "ID",
            "countryName": "Indonesia",
            "harborSize": "L",
            "harborType": "CN",
            "xcoord": 112.733333,
            "ycoord": -7.2,
            "chDepth": "10",
            "anDepth": "12",
            "loWharves": "Y",
            "loContainer": "Y",
            "firstPortOfEntry": "Y",
        },
        {
            "portNumber": 52070,
            "portName": "Balikpapan",
            "countryCode": "ID",
            "countryName": "Indonesia",
            "harborSize": "S",
            "harborType": "CN",
            "xcoord": 116.816667,
            "ycoord": -1.25,
            "chDepth": "13",
            "anDepth": "13",
            "loWharves": "Y",
            "loOilTerm": "Y",
            "firstPortOfEntry": "Y",
        },
    ],
    "Singapore": [
        {
            "portNumber": 50017,
            "portName": "Jurong Island",
            "countryCode": "SG",
            "countryName": "Singapore",
            "harborSize": "L",
            "harborType": "CN",
            "xcoord": 103.733333,
            "ycoord": 1.283333,
            "chDepth": "14",
            "anDepth": "9",
            "cpDepth": "17",
            "otDepth": "17",
            "loWharves": "Y",
            "loLiquidBulk": "Y",
            "firstPortOfEntry": "Y",
        }
    ],
}


def _empty_feature_collection() -> dict[str, Any]:
    return {"type": "FeatureCollection", "features": []}


def _parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_dms(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    match = _DMS_PATTERN.match(value)
    if not match:
        return None
    degrees, minutes, seconds, hemisphere = match.groups()
    decimal = float(degrees) + (float(minutes) / 60.0) + (float(seconds) / 3600.0)
    if hemisphere.upper() in {"S", "W"}:
        decimal *= -1
    return decimal


def _coordinate(raw: dict[str, Any], decimal_key: str, dms_key: str) -> float | None:
    decimal_value = _parse_float(raw.get(decimal_key))
    if decimal_value is not None:
        return decimal_value
    return _parse_dms(raw.get(dms_key))


def _yes_score(value: Any, unknown_score: float = 0.35) -> float:
    normalized = str(value or "U").upper()
    if normalized == "Y":
        return 1.0
    if normalized == "N":
        return 0.0
    return unknown_score


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _depth_score(depth_m: float | None) -> float:
    if depth_m is None:
        return 0.35
    if depth_m >= 14:
        return 1.0
    if depth_m >= 10:
        return 0.78
    if depth_m >= 6:
        return 0.55
    if depth_m >= 3:
        return 0.32
    return 0.15


def _max_depth(raw: dict[str, Any]) -> float | None:
    values = [
        _parse_float(raw.get(key))
        for key in ("chDepth", "anDepth", "cpDepth", "otDepth", "lngTerminalDepth", "offMaxVesselDraft")
    ]
    valid_values = [value for value in values if value is not None]
    return max(valid_values) if valid_values else None


def _port_readiness(raw: dict[str, Any]) -> tuple[float, dict[str, float]]:
    harbor_score = {"L": 1.0, "M": 0.78, "S": 0.58, "V": 0.38}.get(str(raw.get("harborSize") or "").upper(), 0.45)
    depth = _max_depth(raw)
    depth_component = _depth_score(depth)
    cargo_component = _average(
        [
            _yes_score(raw.get("loWharves")),
            _yes_score(raw.get("loContainer")),
            _yes_score(raw.get("loLiquidBulk")),
            _yes_score(raw.get("loOilTerm")),
            _yes_score(raw.get("loSolidBulk")),
            _yes_score(raw.get("loBreakBulk")),
        ]
    )
    operations_component = _average(
        [
            _yes_score(raw.get("firstPortOfEntry")),
            _yes_score(raw.get("tugsAssist")),
            _yes_score(raw.get("cmRadio")),
            _yes_score(raw.get("turningArea")),
            _yes_score(raw.get("etaMessage")),
        ]
    )
    score = round(
        max(
            0.0,
            min(
                1.0,
                (0.30 * harbor_score)
                + (0.30 * depth_component)
                + (0.25 * cargo_component)
                + (0.15 * operations_component),
            ),
        ),
        4,
    )
    return score, {
        "harbor_size_score": round(harbor_score, 4),
        "depth_score": round(depth_component, 4),
        "cargo_handling_score": round(cargo_component, 4),
        "operations_score": round(operations_component, 4),
    }


def _readiness_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.55:
        return "medium"
    return "basic"


def normalize_wpi_port(raw: dict[str, Any], source_mode: str = "wpi_live_api") -> dict[str, Any] | None:
    latitude = _coordinate(raw, "ycoord", "latitude")
    longitude = _coordinate(raw, "xcoord", "longitude")
    if latitude is None or longitude is None:
        return None

    readiness_score, readiness_components = _port_readiness(raw)
    port_number = raw.get("portNumber")
    country_code = raw.get("countryCode") or ""
    return {
        "wpi_id": f"{country_code}-{port_number or raw.get('portName')}",
        "port_number": port_number,
        "port_name": raw.get("portName") or "Unknown port",
        "country_code": country_code,
        "country_name": raw.get("countryName") or "",
        "region_name": raw.get("regionName"),
        "latitude": round(float(latitude), 6),
        "longitude": round(float(longitude), 6),
        "harbor_size": raw.get("harborSize"),
        "harbor_type": raw.get("harborType"),
        "harbor_use": raw.get("harborUse"),
        "channel_depth_m": _parse_float(raw.get("chDepth")),
        "anchorage_depth_m": _parse_float(raw.get("anDepth")),
        "cargo_pier_depth_m": _parse_float(raw.get("cpDepth")),
        "oil_terminal_depth_m": _parse_float(raw.get("otDepth")),
        "max_depth_m": _max_depth(raw),
        "has_wharf": str(raw.get("loWharves") or "U").upper(),
        "has_container": str(raw.get("loContainer") or "U").upper(),
        "has_liquid_bulk": str(raw.get("loLiquidBulk") or "U").upper(),
        "has_oil_terminal": str(raw.get("loOilTerm") or "U").upper(),
        "first_port_of_entry": str(raw.get("firstPortOfEntry") or "U").upper(),
        "tugs_assist": str(raw.get("tugsAssist") or "U").upper(),
        "readiness_score": readiness_score,
        "readiness_label": _readiness_label(readiness_score),
        "readiness_components": readiness_components,
        "unlo_code": raw.get("unloCode"),
        "source": "NGA World Port Index",
        "source_url": WPI_SOURCE_URL,
        "source_mode": source_mode,
    }


def _fetch_wpi_payload(country_name: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"countryName": country_name, "output": "json"})
    request = urllib.request.Request(
        f"{WPI_API_URL}?{query}",
        headers={"User-Agent": "MechWiz/1.0 public-screening"},
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


@lru_cache(maxsize=8)
def load_wpi_ports(country_name: str) -> tuple[dict[str, Any], ...]:
    source_mode = "wpi_live_api"
    try:
        payload = _fetch_wpi_payload(country_name)
        raw_ports = payload.get("ports", [])
    except Exception:
        source_mode = "fallback_static_major_ports"
        raw_ports = FALLBACK_WPI_PORTS.get(country_name, [])

    ports = [
        port
        for port in (normalize_wpi_port(raw_port, source_mode=source_mode) for raw_port in raw_ports)
        if port is not None
    ]
    return tuple(sorted(ports, key=lambda item: (item["country_name"], item["port_name"])))


def haversine_distance_km(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
    earth_radius_km = 6371.0
    phi_a = math.radians(lat_a)
    phi_b = math.radians(lat_b)
    delta_phi = math.radians(lat_b - lat_a)
    delta_lambda = math.radians(lon_b - lon_a)
    a = (math.sin(delta_phi / 2) ** 2) + (math.cos(phi_a) * math.cos(phi_b) * math.sin(delta_lambda / 2) ** 2)
    return 2 * earth_radius_km * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearest_port_to(latitude: float, longitude: float, ports: tuple[dict[str, Any], ...]) -> tuple[dict[str, Any], float] | None:
    if not ports:
        return None
    distances = [
        (
            port,
            haversine_distance_km(latitude, longitude, float(port["latitude"]), float(port["longitude"])),
        )
        for port in ports
    ]
    return min(distances, key=lambda item: item[1])


def _port_proximity_score(distance_km: float | None) -> float:
    if distance_km is None:
        return 0.0
    if distance_km <= 25:
        return 1.0
    if distance_km <= 75:
        return 0.82
    if distance_km <= 150:
        return 0.62
    if distance_km <= 300:
        return 0.42
    return 0.22


def _metric_score(value: float | None, maximum: float) -> float:
    if value is None or maximum <= 0:
        return 0.0
    return max(0.0, min(1.0, float(value) / maximum))


def _economic_label(score: float, is_top_zone: bool = False) -> str:
    if is_top_zone or score >= 0.78:
        return "highest"
    if score >= 0.62:
        return "high"
    if score >= 0.42:
        return "medium"
    return "emerging"


def _row_records(records: list[UnitScoringResult]) -> list[dict[str, Any]]:
    return [ranking_row_from_record(record) for record in records]


def build_port_aware_unit_geojson(records: list[UnitScoringResult]) -> dict[str, Any]:
    rows = _row_records(records)
    ports = load_wpi_ports("Indonesia")
    max_methanol = max((row["methanol_tpy"] or 0 for row in rows), default=0)
    features: list[dict[str, Any]] = []

    for row in rows:
        longitude = row["longitude"]
        latitude = row["latitude"]
        if longitude is None or latitude is None:
            continue

        nearest = nearest_port_to(float(latitude), float(longitude), ports)
        port = nearest[0] if nearest else None
        distance_km = nearest[1] if nearest else None
        proximity_score = _port_proximity_score(distance_km)
        port_readiness = float(port["readiness_score"]) if port else 0.0
        methanol_score = _metric_score(row["methanol_tpy"], max_methanol)
        economic_value_score = round(
            (0.38 * row["composite_score"])
            + (0.24 * methanol_score)
            + (0.22 * port_readiness)
            + (0.16 * proximity_score),
            4,
        )

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
                    "nearest_port_name": port["port_name"] if port else None,
                    "nearest_port_country": port["country_name"] if port else None,
                    "nearest_port_distance_km": round(distance_km, 1) if distance_km is not None else None,
                    "nearest_port_readiness_score": port_readiness,
                    "nearest_port_readiness_label": port["readiness_label"] if port else "unknown",
                    "port_proximity_score": proximity_score,
                    "economic_value_score": economic_value_score,
                    "economic_value_label": _economic_label(economic_value_score),
                    "port_data_source": WPI_SOURCE_URL,
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}


def build_ports_geojson() -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    for country_name in ("Indonesia", "Singapore"):
        for port in load_wpi_ports(country_name):
            is_export_target = country_name == "Singapore" and port["port_name"] == SINGAPORE_TARGET_PORT
            features.append(
                {
                    "type": "Feature",
                    "id": port["wpi_id"],
                    "geometry": {
                        "type": "Point",
                        "coordinates": [port["longitude"], port["latitude"]],
                    },
                    "properties": {
                        **port,
                        "is_export_target": is_export_target,
                    },
                }
            )
    return {"type": "FeatureCollection", "features": features}


def _economic_zone_groups(records: list[UnitScoringResult]) -> list[dict[str, Any]]:
    rows = _row_records(records)
    ports = load_wpi_ports("Indonesia")
    groups: dict[str, dict[str, Any]] = {}

    for row in rows:
        longitude = row["longitude"]
        latitude = row["latitude"]
        if longitude is None or latitude is None:
            continue
        nearest = nearest_port_to(float(latitude), float(longitude), ports)
        if nearest is None:
            continue

        port, distance_km = nearest
        key = str(port["wpi_id"])
        weight = max(float(row["methanol_tpy"] or 0), float(row["co2_tpy"] or 0) * 0.05, float(row["capacity_mw"] or 0), 1.0)
        group = groups.setdefault(
            key,
            {
                "port": port,
                "unit_count": 0,
                "capacity_mw": 0.0,
                "co2_tpy": 0.0,
                "methanol_tpy": 0.0,
                "score_weight": 0.0,
                "score_total": 0.0,
                "distance_total": 0.0,
                "lon_weight_total": 0.0,
                "lat_weight_total": 0.0,
                "coord_weight": 0.0,
                "top_unit": None,
                "top_unit_score": -1.0,
            },
        )
        group["unit_count"] += 1
        group["capacity_mw"] += float(row["capacity_mw"] or 0)
        group["co2_tpy"] += float(row["co2_tpy"] or 0)
        group["methanol_tpy"] += float(row["methanol_tpy"] or 0)
        group["score_weight"] += weight
        group["score_total"] += float(row["composite_score"]) * weight
        group["distance_total"] += distance_km
        group["lon_weight_total"] += float(longitude) * weight
        group["lat_weight_total"] += float(latitude) * weight
        group["coord_weight"] += weight
        if float(row["composite_score"]) > group["top_unit_score"]:
            group["top_unit_score"] = float(row["composite_score"])
            group["top_unit"] = f"{row['site_name']} {row['unit_name']}"

    return list(groups.values())


def build_economic_zones_geojson(records: list[UnitScoringResult]) -> dict[str, Any]:
    groups = _economic_zone_groups(records)
    if not groups:
        return _empty_feature_collection()

    max_methanol = max(group["methanol_tpy"] for group in groups)
    max_co2 = max(group["co2_tpy"] for group in groups)
    max_units = max(group["unit_count"] for group in groups)

    features: list[dict[str, Any]] = []
    for group in groups:
        port = group["port"]
        average_score = group["score_total"] / group["score_weight"] if group["score_weight"] else 0.0
        average_distance = group["distance_total"] / group["unit_count"] if group["unit_count"] else 0.0
        center_lng = group["lon_weight_total"] / group["coord_weight"] if group["coord_weight"] else port["longitude"]
        center_lat = group["lat_weight_total"] / group["coord_weight"] if group["coord_weight"] else port["latitude"]
        proximity_score = _port_proximity_score(average_distance)
        economic_score = round(
            (0.34 * _metric_score(group["methanol_tpy"], max_methanol))
            + (0.18 * _metric_score(group["co2_tpy"], max_co2))
            + (0.16 * average_score)
            + (0.16 * float(port["readiness_score"]))
            + (0.10 * proximity_score)
            + (0.06 * _metric_score(group["unit_count"], max_units)),
            4,
        )
        features.append(
            {
                "type": "Feature",
                "id": f"zone-{port['wpi_id']}",
                "geometry": {
                    "type": "Point",
                    "coordinates": [round(center_lng, 6), round(center_lat, 6)],
                },
                "properties": {
                    "zone_name": f"{port['port_name']} economic zone",
                    "nearest_port_name": port["port_name"],
                    "nearest_port_country": port["country_name"],
                    "nearest_port_longitude": port["longitude"],
                    "nearest_port_latitude": port["latitude"],
                    "nearest_port_readiness_score": port["readiness_score"],
                    "nearest_port_readiness_label": port["readiness_label"],
                    "average_port_distance_km": round(average_distance, 1),
                    "port_proximity_score": proximity_score,
                    "unit_count": group["unit_count"],
                    "capacity_mw": round(group["capacity_mw"], 1),
                    "co2_tpy": round(group["co2_tpy"], 1),
                    "methanol_tpy": round(group["methanol_tpy"], 1),
                    "average_composite_score": round(average_score, 4),
                    "economic_score": economic_score,
                    "economic_label": _economic_label(economic_score),
                    "zone_radius": round(22 + (72 * economic_score) + (3 * math.log1p(group["unit_count"])), 1),
                    "top_unit": group["top_unit"],
                    "source": "GEM unit screening plus NGA World Port Index",
                    "source_url": WPI_SOURCE_URL,
                },
            }
        )

    features.sort(key=lambda feature: feature["properties"]["economic_score"], reverse=True)
    if features:
        features[0]["properties"]["economic_label"] = _economic_label(
            float(features[0]["properties"]["economic_score"]), is_top_zone=True
        )
    return {"type": "FeatureCollection", "features": features}


def _singapore_target_port() -> dict[str, Any] | None:
    singapore_ports = load_wpi_ports("Singapore")
    for port in singapore_ports:
        if port["port_name"] == SINGAPORE_TARGET_PORT:
            return port
    return singapore_ports[0] if singapore_ports else None


def build_export_corridors_geojson(records: list[UnitScoringResult], limit: int = 6) -> dict[str, Any]:
    zones = build_economic_zones_geojson(records)["features"]
    target_port = _singapore_target_port()
    if not zones or target_port is None:
        return _empty_feature_collection()

    features: list[dict[str, Any]] = []
    for zone in zones[:limit]:
        properties = zone["properties"]
        source_lat = float(properties["nearest_port_latitude"])
        source_lng = float(properties["nearest_port_longitude"])
        target_lat = float(target_port["latitude"])
        target_lng = float(target_port["longitude"])
        distance_km = haversine_distance_km(source_lat, source_lng, target_lat, target_lng)
        features.append(
            {
                "type": "Feature",
                "id": f"corridor-{properties['nearest_port_name']}-{target_port['port_name']}",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [round(source_lng, 6), round(source_lat, 6)],
                        [round(target_lng, 6), round(target_lat, 6)],
                    ],
                },
                "properties": {
                    "source_port_name": properties["nearest_port_name"],
                    "target_port_name": target_port["port_name"],
                    "target_country": target_port["country_name"],
                    "zone_name": properties["zone_name"],
                    "economic_score": properties["economic_score"],
                    "economic_label": properties["economic_label"],
                    "methanol_tpy": properties["methanol_tpy"],
                    "unit_count": properties["unit_count"],
                    "straight_line_distance_km": round(distance_km, 1),
                    "indicative_sea_distance_km": round(distance_km * 1.18, 1),
                    "route_type": "screening_proxy_straight_line",
                    "demand_reference": "Singapore MPA methanol marine fuel demand can potentially exceed 1 MTPA before 2030.",
                    "demand_reference_url": SINGAPORE_METHANOL_REFERENCE_URL,
                    "source": "NGA World Port Index and public screening model",
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}

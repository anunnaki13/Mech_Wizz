from typing import Any

from sqlalchemy.orm import Session

from app.services.port_intelligence import load_wpi_ports, nearest_port_to
from app.services.scoring import latest_scoring_records, ranking_row_from_record


SHORTLIST_WEIGHTS = {
    "screening": 0.35,
    "economics": 0.25,
    "logistics": 0.20,
    "confidence": 0.20,
}


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def _metric_score(value: float | None, maximum: float) -> float:
    if value is None or maximum <= 0:
        return 0.0
    return _bounded(float(value) / maximum)


def _lower_is_better_score(value: float | None, minimum: float | None, maximum: float | None) -> float:
    if value is None or minimum is None or maximum is None:
        return 0.35
    if maximum <= minimum:
        return 0.75
    return _bounded(1 - ((float(value) - minimum) / (maximum - minimum)))


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


def _commercial_ports(ports: tuple[dict[str, Any], ...]) -> tuple[dict[str, Any], ...]:
    filtered = [
        port
        for port in ports
        if "oil field" not in str(port.get("port_name", "")).lower()
        and (
            port.get("has_wharf") == "Y"
            or port.get("has_container") == "Y"
            or port.get("has_liquid_bulk") == "Y"
            or port.get("has_oil_terminal") == "Y"
        )
    ]
    return tuple(filtered) or ports


def _readiness_label(score: float) -> str:
    if score >= 0.75:
        return "ready_for_top3_validation"
    if score >= 0.62:
        return "validate_next"
    if score >= 0.48:
        return "watchlist"
    return "defer"


def _recommendation(shortlist_rank: int, top_n: int) -> str:
    if shortlist_rank <= 3:
        return "shortlist_top3"
    if shortlist_rank <= top_n:
        return "shortlist_top5"
    return "watchlist"


def _rationale(row: dict[str, Any], logistics_score: float, economics_score: float, confidence_score: float) -> list[str]:
    reasons: list[str] = []
    if row["methanol_tpy"]:
        reasons.append("Large e-methanol production potential relative to the current candidate set.")
    if row["captured_co2_tpy"]:
        reasons.append("Material captured CO2 volume for pilot-to-scale screening.")
    if logistics_score >= 0.70:
        reasons.append("Port proximity/readiness supports export-oriented validation.")
    elif logistics_score < 0.45:
        reasons.append("Logistics require closer port and handling validation.")
    if economics_score >= 0.65:
        reasons.append("Economic benchmark is competitive within the screening dataset.")
    if confidence_score < 0.50:
        reasons.append("Data confidence still limits decision certainty.")
    return reasons[:4]


def _next_actions(row: dict[str, Any], distance_km: float | None, confidence_score: float) -> list[str]:
    actions: list[str] = []
    if row["data_gap_count"] > 0:
        actions.append("Close high-impact data gaps and confirm source documents.")
    if distance_km is None:
        actions.append("Confirm nearest feasible export port and transport route.")
    elif distance_km > 150:
        actions.append("Validate trucking/jetty/sea logistics cost before Top 3 decision.")
    else:
        actions.append("Request port handling confirmation for methanol export scenario.")
    if row["estimated_lcom_usd_ton"] is None:
        actions.append("Validate CAPEX/OPEX package so LCOM can be investment-grade.")
    if confidence_score < 0.55:
        actions.append("Upgrade public/benchmark data to PLN or site-verified data.")
    return actions[:4]


def build_shortlist_decision_matrix(db: Session, scheme: str = "align", top_n: int = 5) -> dict[str, Any]:
    records = latest_scoring_records(db, scheme=scheme)
    rows = [ranking_row_from_record(record) for record in records]
    ports = _commercial_ports(load_wpi_ports("Indonesia"))

    max_revenue = max((row["gross_revenue_usd_per_year"] or 0 for row in rows), default=0)
    max_methanol = max((row["methanol_tpy"] or 0 for row in rows), default=0)
    lcom_values = [float(row["estimated_lcom_usd_ton"]) for row in rows if row["estimated_lcom_usd_ton"] is not None]
    min_lcom = min(lcom_values) if lcom_values else None
    max_lcom = max(lcom_values) if lcom_values else None

    candidates: list[dict[str, Any]] = []
    for row in rows:
        latitude = row["latitude"]
        longitude = row["longitude"]
        nearest = nearest_port_to(float(latitude), float(longitude), ports) if latitude is not None and longitude is not None else None
        port = nearest[0] if nearest else None
        distance_km = nearest[1] if nearest else None
        port_readiness = float(port["readiness_score"]) if port else 0.0
        proximity_score = _port_proximity_score(distance_km)
        logistics_score = _bounded((0.58 * port_readiness) + (0.42 * proximity_score))

        revenue_score = _metric_score(row["gross_revenue_usd_per_year"], max_revenue)
        methanol_score = _metric_score(row["methanol_tpy"], max_methanol)
        lcom_score = _lower_is_better_score(row["estimated_lcom_usd_ton"], min_lcom, max_lcom)
        economics_score = _bounded((0.42 * revenue_score) + (0.34 * methanol_score) + (0.24 * lcom_score))

        confidence_score = _bounded(float(row["confidence_score"]) - (0.025 * int(row["data_gap_count"])))
        final_score = _bounded(
            (SHORTLIST_WEIGHTS["screening"] * float(row["composite_score"]))
            + (SHORTLIST_WEIGHTS["economics"] * economics_score)
            + (SHORTLIST_WEIGHTS["logistics"] * logistics_score)
            + (SHORTLIST_WEIGHTS["confidence"] * confidence_score)
        )

        candidates.append(
            {
                "plant_id": row["plant_id"],
                "scenario_id": row["scenario_id"],
                "scenario_result_id": row["scenario_result_id"],
                "site_name": row["site_name"],
                "unit_name": row["unit_name"],
                "province": row["province"],
                "city": row["city"],
                "capacity_mw": row["capacity_mw"],
                "screening_rank": row["rank"],
                "composite_score": row["composite_score"],
                "co2_tpy": row["co2_tpy"],
                "captured_co2_tpy": row["captured_co2_tpy"],
                "methanol_tpy": row["methanol_tpy"],
                "h2_required_tpy": row["h2_required_tpy"],
                "electrolyzer_required_mw": row["electrolyzer_required_mw"],
                "gross_revenue_usd_per_year": row["gross_revenue_usd_per_year"],
                "estimated_lcom_usd_ton": row["estimated_lcom_usd_ton"],
                "nearest_port_name": port["port_name"] if port else None,
                "nearest_port_distance_km": round(distance_km, 1) if distance_km is not None else None,
                "nearest_port_readiness_score": round(port_readiness, 4),
                "port_proximity_score": proximity_score,
                "score_breakdown": {
                    "screening_score": round(float(row["composite_score"]), 4),
                    "economics_score": economics_score,
                    "logistics_score": logistics_score,
                    "confidence_score": confidence_score,
                    "final_score": final_score,
                },
                "data_confidence_label": row["data_confidence_label"],
                "data_gap_count": row["data_gap_count"],
                "key_bottleneck": row["key_bottleneck"],
            }
        )

    candidates.sort(key=lambda item: item["score_breakdown"]["final_score"], reverse=True)
    for index, candidate in enumerate(candidates, start=1):
        final_score = candidate["score_breakdown"]["final_score"]
        candidate["shortlist_rank"] = index
        candidate["recommendation"] = _recommendation(index, top_n)
        candidate["readiness_label"] = _readiness_label(final_score)
        candidate["decision_rationale"] = _rationale(
            candidate,
            candidate["score_breakdown"]["logistics_score"],
            candidate["score_breakdown"]["economics_score"],
            candidate["score_breakdown"]["confidence_score"],
        )
        candidate["next_actions"] = _next_actions(
            candidate,
            candidate["nearest_port_distance_km"],
            candidate["score_breakdown"]["confidence_score"],
        )

    shortlist = candidates[:top_n]
    lcom_shortlist = [
        float(candidate["estimated_lcom_usd_ton"])
        for candidate in shortlist
        if candidate["estimated_lcom_usd_ton"] is not None
    ]
    summary = {
        "candidate_count": len(candidates),
        "shortlist_count": len(shortlist),
        "top_candidate": candidates[0]["site_name"] if candidates else None,
        "top_score": candidates[0]["score_breakdown"]["final_score"] if candidates else None,
        "shortlist_captured_co2_tpy": round(sum(float(candidate["captured_co2_tpy"] or 0) for candidate in shortlist), 2),
        "shortlist_methanol_tpy": round(sum(float(candidate["methanol_tpy"] or 0) for candidate in shortlist), 2),
        "shortlist_gross_revenue_usd_per_year": round(
            sum(float(candidate["gross_revenue_usd_per_year"] or 0) for candidate in shortlist),
            2,
        ),
        "average_shortlist_lcom_usd_ton": round(sum(lcom_shortlist) / len(lcom_shortlist), 2) if lcom_shortlist else None,
    }
    warnings = [
        "Shortlist score is a screening decision aid, not a final investment approval.",
        "Port distance is a straight-line proxy and must be replaced with route, terminal, and handling confirmation.",
        "Economics use current deterministic scenario outputs; vendor quotes and PLN-verified site data should replace benchmark assumptions.",
    ]

    return {
        "scheme": scheme,
        "top_n": top_n,
        "method": "0.35 screening + 0.25 economics + 0.20 logistics + 0.20 confidence",
        "weights": SHORTLIST_WEIGHTS,
        "summary": summary,
        "candidates": candidates,
        "warnings": warnings,
    }

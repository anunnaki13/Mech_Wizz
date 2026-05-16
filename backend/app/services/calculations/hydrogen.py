from app.services.calculations.defaults import (
    DEFAULT_H2_PRODUCTIVITY_KG_DAY_PER_MW,
    DEFAULT_H2_UTILIZATION_FACTOR,
    H2_PER_METHANOL_TON,
)


def _missing(*values: float | int | None) -> bool:
    return any(value is None for value in values)


def _positive(name: str, value: float | int) -> float:
    numeric = float(value)
    if numeric <= 0:
        raise ValueError(f"{name} must be positive")
    return numeric


def _non_negative(name: str, value: float | int) -> float:
    numeric = float(value)
    if numeric < 0:
        raise ValueError(f"{name} must be non-negative")
    return numeric


def calculate_h2_required_ton_year(
    methanol_actual_ton_year: float | None,
    h2_utilization_factor: float | None = DEFAULT_H2_UTILIZATION_FACTOR,
) -> float | None:
    if _missing(methanol_actual_ton_year, h2_utilization_factor):
        return None
    methanol = _non_negative("methanol_actual_ton_year", methanol_actual_ton_year)
    utilization = _positive("h2_utilization_factor", h2_utilization_factor)
    if utilization > 1:
        raise ValueError("h2_utilization_factor must be <= 1")
    return methanol * H2_PER_METHANOL_TON / utilization


def calculate_electrolyzer_mw(
    h2_required_ton_year: float | None,
    operating_days_per_year: int | float | None,
    h2_productivity_kg_day_per_mw: float | None = DEFAULT_H2_PRODUCTIVITY_KG_DAY_PER_MW,
) -> float | None:
    if _missing(h2_required_ton_year, operating_days_per_year, h2_productivity_kg_day_per_mw):
        return None
    h2_required = _non_negative("h2_required_ton_year", h2_required_ton_year)
    operating_days = _positive("operating_days_per_year", operating_days_per_year)
    productivity = _positive("h2_productivity_kg_day_per_mw", h2_productivity_kg_day_per_mw)
    return (h2_required * 1000 / operating_days) / productivity

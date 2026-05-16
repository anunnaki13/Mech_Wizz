from collections.abc import Iterable, Mapping
import math
from typing import Any

from app.services.calculations.defaults import CO2_DENSITY_KG_NM3


def _none_if_missing(*values: float | int | None) -> bool:
    return any(value is None for value in values)


def _require_non_negative(name: str, value: float | int) -> float:
    numeric = float(value)
    if numeric < 0:
        raise ValueError(f"{name} must be non-negative")
    return numeric


def _value(record: Mapping[str, Any] | object, field: str) -> Any:
    if isinstance(record, Mapping):
        return record.get(field)
    return getattr(record, field, None)


def calculate_stack_area_m2(diameter_m: float | None) -> float | None:
    if diameter_m is None:
        return None
    diameter = _require_non_negative("diameter_m", diameter_m)
    return math.pi * (diameter / 2) ** 2


def calculate_normalized_gas_flow_nm3_s(
    velocity_m_s: float | None,
    area_m2: float | None,
    temperature_c: float | None,
) -> float | None:
    if _none_if_missing(velocity_m_s, area_m2, temperature_c):
        return None
    velocity = _require_non_negative("velocity_m_s", velocity_m_s)
    area = _require_non_negative("area_m2", area_m2)
    temperature = float(temperature_c)
    if temperature <= -273.15:
        raise ValueError("temperature_c must be greater than absolute zero")
    return velocity * area * (273.15 / (273.15 + temperature))


def calculate_co2_wet_fraction(co2_percent_dry: float | None, moisture_percent: float | None) -> float | None:
    if _none_if_missing(co2_percent_dry, moisture_percent):
        return None
    co2_dry = _require_non_negative("co2_percent_dry", co2_percent_dry)
    moisture = _require_non_negative("moisture_percent", moisture_percent)
    if co2_dry > 100:
        raise ValueError("co2_percent_dry must be <= 100")
    if moisture > 100:
        raise ValueError("moisture_percent must be <= 100")
    return (co2_dry / 100) * (1 - moisture / 100)


def calculate_co2_kg_s(
    normal_flow_nm3_s: float | None,
    co2_wet_fraction: float | None,
    co2_density_kg_nm3: float = CO2_DENSITY_KG_NM3,
) -> float | None:
    if _none_if_missing(normal_flow_nm3_s, co2_wet_fraction, co2_density_kg_nm3):
        return None
    normal_flow = _require_non_negative("normal_flow_nm3_s", normal_flow_nm3_s)
    fraction = _require_non_negative("co2_wet_fraction", co2_wet_fraction)
    density = _require_non_negative("co2_density_kg_nm3", co2_density_kg_nm3)
    if fraction > 1:
        raise ValueError("co2_wet_fraction must be <= 1")
    return normal_flow * fraction * density


def calculate_co2_ton_day(co2_kg_s: float | None) -> float | None:
    if co2_kg_s is None:
        return None
    kg_s = _require_non_negative("co2_kg_s", co2_kg_s)
    return kg_s * 86400 / 1000


def calculate_co2_ton_year(co2_ton_day: float | None, operating_days_per_year: int | float | None) -> float | None:
    if _none_if_missing(co2_ton_day, operating_days_per_year):
        return None
    ton_day = _require_non_negative("co2_ton_day", co2_ton_day)
    operating_days = _require_non_negative("operating_days_per_year", operating_days_per_year)
    if operating_days > 366:
        raise ValueError("operating_days_per_year must be <= 366")
    return ton_day * operating_days


def calculate_emission_test_co2_ton_year(
    emission_test: Mapping[str, Any] | object,
    operating_days_per_year: int | float | None,
) -> float | None:
    area = calculate_stack_area_m2(_value(emission_test, "stack_diameter_m"))
    normal_flow = calculate_normalized_gas_flow_nm3_s(
        _value(emission_test, "gas_velocity_m_s"),
        area,
        _value(emission_test, "flue_gas_temperature_c"),
    )
    wet_fraction = calculate_co2_wet_fraction(
        _value(emission_test, "co2_percent_dry"),
        _value(emission_test, "moisture_percent"),
    )
    co2_kg_s = calculate_co2_kg_s(normal_flow, wet_fraction)
    co2_ton_day = calculate_co2_ton_day(co2_kg_s)
    return calculate_co2_ton_year(co2_ton_day, operating_days_per_year)


def calculate_total_co2_ton_year(
    emission_tests: Iterable[Mapping[str, Any] | object],
    operating_days_per_year: int | float | None,
) -> float | None:
    total = 0.0
    valid_count = 0
    for emission_test in emission_tests:
        value = calculate_emission_test_co2_ton_year(emission_test, operating_days_per_year)
        if value is not None:
            total += value
            valid_count += 1
    return total if valid_count else None

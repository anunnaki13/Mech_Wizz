from app.services.calculations.defaults import CO2_TO_METHANOL_TON_FACTOR, DEFAULT_PROCESS_EFFICIENCY


def _missing(*values: float | None) -> bool:
    return any(value is None for value in values)


def _non_negative(name: str, value: float) -> float:
    numeric = float(value)
    if numeric < 0:
        raise ValueError(f"{name} must be non-negative")
    return numeric


def calculate_captured_co2_ton_year(total_co2_ton_year: float | None, capture_rate: float | None) -> float | None:
    if _missing(total_co2_ton_year, capture_rate):
        return None
    total = _non_negative("total_co2_ton_year", total_co2_ton_year)
    rate = _non_negative("capture_rate", capture_rate)
    if rate > 1:
        raise ValueError("capture_rate must be <= 1")
    return total * rate


def calculate_vented_co2_ton_year(total_co2_ton_year: float | None, captured_co2_ton_year: float | None) -> float | None:
    if _missing(total_co2_ton_year, captured_co2_ton_year):
        return None
    total = _non_negative("total_co2_ton_year", total_co2_ton_year)
    captured = _non_negative("captured_co2_ton_year", captured_co2_ton_year)
    if captured > total:
        raise ValueError("captured_co2_ton_year must be <= total_co2_ton_year")
    return total - captured


def calculate_methanol_theoretical_ton_year(captured_co2_ton_year: float | None) -> float | None:
    if captured_co2_ton_year is None:
        return None
    captured = _non_negative("captured_co2_ton_year", captured_co2_ton_year)
    return captured * CO2_TO_METHANOL_TON_FACTOR


def calculate_methanol_actual_ton_year(
    methanol_theoretical_ton_year: float | None,
    process_efficiency: float | None = DEFAULT_PROCESS_EFFICIENCY,
) -> float | None:
    if _missing(methanol_theoretical_ton_year, process_efficiency):
        return None
    theoretical = _non_negative("methanol_theoretical_ton_year", methanol_theoretical_ton_year)
    efficiency = _non_negative("process_efficiency", process_efficiency)
    if efficiency > 1:
        raise ValueError("process_efficiency must be <= 1")
    return theoretical * efficiency

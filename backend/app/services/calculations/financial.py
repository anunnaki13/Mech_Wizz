from collections.abc import Sequence

from app.services.calculations.defaults import DEFAULT_PROJECT_LIFE_YEARS


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


def calculate_carbon_credit_price_usd_per_ton(
    carbon_credit_price_idr_per_ton: float | None,
    exchange_rate_idr_usd: float | None,
) -> float | None:
    if _missing(carbon_credit_price_idr_per_ton, exchange_rate_idr_usd):
        return None
    price_idr = _non_negative("carbon_credit_price_idr_per_ton", carbon_credit_price_idr_per_ton)
    exchange_rate = _positive("exchange_rate_idr_usd", exchange_rate_idr_usd)
    return price_idr / exchange_rate


def calculate_gross_revenue_usd_per_year(
    methanol_ton_year: float | None,
    methanol_price_usd_per_ton: float | None,
    captured_co2_ton_year: float | None,
    carbon_credit_price_usd_per_ton: float | None,
    asset_revenue_usd_per_year: float | None = 0.0,
) -> float | None:
    if _missing(
        methanol_ton_year,
        methanol_price_usd_per_ton,
        captured_co2_ton_year,
        carbon_credit_price_usd_per_ton,
        asset_revenue_usd_per_year,
    ):
        return None
    methanol = _non_negative("methanol_ton_year", methanol_ton_year)
    methanol_price = _non_negative("methanol_price_usd_per_ton", methanol_price_usd_per_ton)
    captured_co2 = _non_negative("captured_co2_ton_year", captured_co2_ton_year)
    carbon_price = _non_negative("carbon_credit_price_usd_per_ton", carbon_credit_price_usd_per_ton)
    asset_revenue = _non_negative("asset_revenue_usd_per_year", asset_revenue_usd_per_year)
    return methanol * methanol_price + captured_co2 * carbon_price + asset_revenue


def calculate_total_capex_usd(*capex_values: float | None) -> float | None:
    if not capex_values or any(value is None for value in capex_values):
        return None
    return sum(_non_negative("capex", value) for value in capex_values)


def calculate_annualized_capex_usd(
    total_capex_usd: float | None,
    discount_rate: float | None,
    project_life_years: int = DEFAULT_PROJECT_LIFE_YEARS,
) -> float | None:
    if _missing(total_capex_usd, discount_rate, project_life_years):
        return None
    capex = _non_negative("total_capex_usd", total_capex_usd)
    rate = _non_negative("discount_rate", discount_rate)
    years = int(_positive("project_life_years", project_life_years))
    if rate == 0:
        return capex / years
    factor = (rate * (1 + rate) ** years) / ((1 + rate) ** years - 1)
    return capex * factor


def calculate_annual_opex_usd(total_capex_usd: float | None, opex_percent_capex: float | None) -> float | None:
    if _missing(total_capex_usd, opex_percent_capex):
        return None
    capex = _non_negative("total_capex_usd", total_capex_usd)
    opex_percent = _non_negative("opex_percent_capex", opex_percent_capex)
    return capex * opex_percent


def calculate_h2_cost_usd_per_year(
    h2_required_ton_year: float | None,
    hydrogen_price_usd_per_kg: float | None,
) -> float | None:
    if _missing(h2_required_ton_year, hydrogen_price_usd_per_kg):
        return None
    h2_required = _non_negative("h2_required_ton_year", h2_required_ton_year)
    price = _non_negative("hydrogen_price_usd_per_kg", hydrogen_price_usd_per_kg)
    return h2_required * 1000 * price


def calculate_electricity_cost_usd_per_year(
    electrolyzer_mw: float | None,
    operating_days_per_year: int | float | None,
    electricity_price_usd_per_kwh: float | None,
) -> float | None:
    if _missing(electrolyzer_mw, operating_days_per_year, electricity_price_usd_per_kwh):
        return None
    electrolyzer = _non_negative("electrolyzer_mw", electrolyzer_mw)
    days = _positive("operating_days_per_year", operating_days_per_year)
    price = _non_negative("electricity_price_usd_per_kwh", electricity_price_usd_per_kwh)
    return electrolyzer * 1000 * 24 * days * price


def calculate_lcom_usd_per_ton(
    methanol_ton_year: float | None,
    annualized_capex_usd: float | None,
    annual_opex_usd: float | None,
    annual_h2_cost_usd: float | None,
    annual_electricity_cost_usd: float | None,
) -> float | None:
    if _missing(
        methanol_ton_year,
        annualized_capex_usd,
        annual_opex_usd,
        annual_h2_cost_usd,
        annual_electricity_cost_usd,
    ):
        return None
    methanol = _positive("methanol_ton_year", methanol_ton_year)
    return (
        _non_negative("annualized_capex_usd", annualized_capex_usd)
        + _non_negative("annual_opex_usd", annual_opex_usd)
        + _non_negative("annual_h2_cost_usd", annual_h2_cost_usd)
        + _non_negative("annual_electricity_cost_usd", annual_electricity_cost_usd)
    ) / methanol


def calculate_annual_cashflow_usd(
    gross_revenue_usd_per_year: float | None,
    annual_opex_usd: float | None,
    annual_h2_cost_usd: float | None,
    annual_electricity_cost_usd: float | None,
    tax_rate: float | None,
) -> float | None:
    if _missing(
        gross_revenue_usd_per_year,
        annual_opex_usd,
        annual_h2_cost_usd,
        annual_electricity_cost_usd,
        tax_rate,
    ):
        return None
    gross = _non_negative("gross_revenue_usd_per_year", gross_revenue_usd_per_year)
    operating_costs = (
        _non_negative("annual_opex_usd", annual_opex_usd)
        + _non_negative("annual_h2_cost_usd", annual_h2_cost_usd)
        + _non_negative("annual_electricity_cost_usd", annual_electricity_cost_usd)
    )
    tax = _non_negative("tax_rate", tax_rate)
    if tax > 1:
        raise ValueError("tax_rate must be <= 1")
    taxable_income = gross - operating_costs
    return taxable_income if taxable_income <= 0 else taxable_income * (1 - tax)


def calculate_npv(
    initial_investment_usd: float | None,
    annual_cashflow_usd: float | None,
    discount_rate: float | None,
    project_life_years: int = DEFAULT_PROJECT_LIFE_YEARS,
) -> float | None:
    if _missing(initial_investment_usd, annual_cashflow_usd, discount_rate, project_life_years):
        return None
    initial = _non_negative("initial_investment_usd", initial_investment_usd)
    annual_cashflow = float(annual_cashflow_usd)
    rate = _non_negative("discount_rate", discount_rate)
    years = int(_positive("project_life_years", project_life_years))
    return sum(annual_cashflow / ((1 + rate) ** year) for year in range(1, years + 1)) - initial


def _npv_for_cashflows(cashflows: Sequence[float], rate: float) -> float:
    return sum(cashflow / ((1 + rate) ** index) for index, cashflow in enumerate(cashflows))


def calculate_irr(cashflows: Sequence[float] | None, precision: float = 1e-7, max_iterations: int = 200) -> float | None:
    if not cashflows or len(cashflows) < 2:
        return None
    if not any(cashflow < 0 for cashflow in cashflows) or not any(cashflow > 0 for cashflow in cashflows):
        return None

    low = -0.9999
    high = 10.0
    low_npv = _npv_for_cashflows(cashflows, low)
    high_npv = _npv_for_cashflows(cashflows, high)
    if low_npv * high_npv > 0:
        return None

    for _ in range(max_iterations):
        mid = (low + high) / 2
        value = _npv_for_cashflows(cashflows, mid)
        if abs(value) <= precision:
            return mid
        if low_npv * value < 0:
            high = mid
            high_npv = value
        else:
            low = mid
            low_npv = value

    return (low + high) / 2


def calculate_project_irr(
    initial_investment_usd: float | None,
    annual_cashflow_usd: float | None,
    project_life_years: int = DEFAULT_PROJECT_LIFE_YEARS,
) -> float | None:
    if _missing(initial_investment_usd, annual_cashflow_usd, project_life_years):
        return None
    initial = float(initial_investment_usd)
    if initial <= 0:
        return None
    years = int(_positive("project_life_years", project_life_years))
    annual_cashflow = float(annual_cashflow_usd)
    return calculate_irr([-initial, *([annual_cashflow] * years)])


def calculate_payback_years(initial_investment_usd: float | None, annual_cashflow_usd: float | None) -> float | None:
    if _missing(initial_investment_usd, annual_cashflow_usd):
        return None
    initial = float(initial_investment_usd)
    annual_cashflow = float(annual_cashflow_usd)
    if initial <= 0 or annual_cashflow <= 0:
        return None
    return initial / annual_cashflow

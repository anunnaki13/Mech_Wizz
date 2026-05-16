from types import SimpleNamespace
import math

import pytest

from app.services.calculations.co2 import (
    calculate_co2_kg_s,
    calculate_co2_ton_day,
    calculate_co2_ton_year,
    calculate_co2_wet_fraction,
    calculate_normalized_gas_flow_nm3_s,
    calculate_stack_area_m2,
    calculate_total_co2_ton_year,
)
from app.services.calculations.financial import (
    calculate_annual_cashflow_usd,
    calculate_annual_opex_usd,
    calculate_annualized_capex_usd,
    calculate_carbon_credit_price_usd_per_ton,
    calculate_electricity_cost_usd_per_year,
    calculate_gross_revenue_usd_per_year,
    calculate_h2_cost_usd_per_year,
    calculate_irr,
    calculate_lcom_usd_per_ton,
    calculate_npv,
    calculate_payback_years,
    calculate_project_irr,
    calculate_total_capex_usd,
)
from app.services.calculations.hydrogen import calculate_electrolyzer_mw, calculate_h2_required_ton_year
from app.services.calculations.methanol import (
    calculate_captured_co2_ton_year,
    calculate_methanol_actual_ton_year,
    calculate_methanol_theoretical_ton_year,
    calculate_vented_co2_ton_year,
)


def test_calculate_co2_ton_year() -> None:
    assert calculate_stack_area_m2(3.0) == pytest.approx(math.pi * 1.5**2)

    area = calculate_stack_area_m2(3.0)
    normal_flow = calculate_normalized_gas_flow_nm3_s(14.4, area, 124)
    assert normal_flow == pytest.approx(14.4 * area * (273.15 / (273.15 + 124)))

    wet_fraction = calculate_co2_wet_fraction(8.48, 5.84)
    assert wet_fraction == pytest.approx(0.0848 * (1 - 0.0584))

    co2_kg_s = calculate_co2_kg_s(normal_flow, wet_fraction)
    assert co2_kg_s == pytest.approx(normal_flow * wet_fraction * 1.964)
    assert calculate_co2_ton_day(1) == pytest.approx(86.4)
    assert calculate_co2_ton_year(86.4, 330) == pytest.approx(28512)


def test_co2_aggregate_skips_missing_records_and_validates_ranges() -> None:
    valid = SimpleNamespace(
        stack_diameter_m=3.0,
        gas_velocity_m_s=14.4,
        flue_gas_temperature_c=124,
        co2_percent_dry=8.48,
        moisture_percent=5.84,
    )
    missing = SimpleNamespace(
        stack_diameter_m=None,
        gas_velocity_m_s=14.4,
        flue_gas_temperature_c=124,
        co2_percent_dry=8.48,
        moisture_percent=5.84,
    )

    total = calculate_total_co2_ton_year([valid, missing], 330)
    assert total is not None
    assert total > 0

    with pytest.raises(ValueError):
        calculate_co2_wet_fraction(101, 5)


def test_methanol_and_hydrogen_calculations() -> None:
    captured = calculate_captured_co2_ton_year(1000, 0.85)
    assert captured == pytest.approx(850)
    assert calculate_vented_co2_ton_year(1000, captured) == pytest.approx(150)

    theoretical = calculate_methanol_theoretical_ton_year(captured)
    assert theoretical == pytest.approx(850 * 0.7273)

    actual = calculate_methanol_actual_ton_year(theoretical, 0.60)
    assert actual == pytest.approx(850 * 0.7273 * 0.60)

    h2_required = calculate_h2_required_ton_year(actual)
    assert h2_required == pytest.approx(actual * 0.1875 / 0.90)
    assert calculate_electrolyzer_mw(h2_required, 330) == pytest.approx((h2_required * 1000 / 330) / 480)


def test_financial_calculations_complete_assumptions_case() -> None:
    carbon_price_usd = calculate_carbon_credit_price_usd_per_ton(58800, 17500)
    assert carbon_price_usd == pytest.approx(3.36)

    gross_revenue = calculate_gross_revenue_usd_per_year(1000, 1250, 850, carbon_price_usd)
    assert gross_revenue == pytest.approx(1_252_856)

    total_capex = calculate_total_capex_usd(2_000_000, 5_000_000, 3_000_000, 1_000_000)
    assert total_capex == pytest.approx(11_000_000)

    annualized_capex = calculate_annualized_capex_usd(total_capex, 0.10, 20)
    annual_opex = calculate_annual_opex_usd(total_capex, 0.04)
    annual_h2_cost = calculate_h2_cost_usd_per_year(200, 3.0)
    annual_electricity_cost = calculate_electricity_cost_usd_per_year(10, 330, 0.06)

    assert annualized_capex == pytest.approx(1_292_056.97, rel=1e-4)
    assert annual_opex == pytest.approx(440_000)
    assert annual_h2_cost == pytest.approx(600_000)
    assert annual_electricity_cost == pytest.approx(4_752_000)

    lcom = calculate_lcom_usd_per_ton(1000, annualized_capex, annual_opex, annual_h2_cost, annual_electricity_cost)
    assert lcom == pytest.approx(7084.05697, rel=1e-4)

    annual_cashflow = calculate_annual_cashflow_usd(gross_revenue, annual_opex, annual_h2_cost, 100_000, 0.22)
    assert annual_cashflow == pytest.approx(88_027.68)


def test_npv_irr_and_payback() -> None:
    npv = calculate_npv(1000, 300, 0.10, 5)
    assert npv == pytest.approx(137.236, rel=1e-4)

    irr = calculate_project_irr(1000, 300, 5)
    assert irr == pytest.approx(0.1524, rel=1e-3)
    assert calculate_irr([-1000, 300, 300, 300, 300, 300]) == pytest.approx(irr)
    assert calculate_payback_years(1000, 300) == pytest.approx(3.3333, rel=1e-4)


def test_invalid_or_incomplete_financial_outputs_return_none() -> None:
    assert calculate_total_capex_usd(1_000_000, None) is None
    assert calculate_lcom_usd_per_ton(1000, None, 100, 100, 100) is None
    assert calculate_irr([100, 200, 300]) is None
    assert calculate_project_irr(1000, -10, 5) is None
    assert calculate_payback_years(1000, 0) is None

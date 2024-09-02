# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 2024

@author: Benedikt Goodman
"""

import pytest
import numpy as np
import pandas as pd

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from functions.calc_funcs import (  # noqa: E402
    loan_calc,
    calculate_govt_support,
    calculate_electricity_costs,
    scenario_analysis_electricity_costs,
    interest_rate_sensitivity,
    monthly_price_calculator,
    monthly_price_calculator_scenarios,
)


def test_loan_calc():
    assert pytest.approx(loan_calc(100000, 0.05, 360), 0.01) == 536.82
    assert pytest.approx(loan_calc(200000, 0.03, 240), 0.01) == 1108.86


def test_calculate_govt_support():
    assert pytest.approx(calculate_govt_support(1000, 1.5, 0.9125), 0.01) == 527.25
    assert (
        calculate_govt_support(6000, 1.5, 0.9125) == 0
    )  # No support for usage > 5000 kWh


def test_calculate_electricity_costs():
    # Test case for no gvmt support
    assert (
        pytest.approx(calculate_electricity_costs(1000, 1, 0, 100, 1), 0.01)
        == 1100
    )
    assert (
        pytest.approx(calculate_electricity_costs(1000, 1.5, 0.1, 100, 0.9125), 0.01)
        == 1171.25
    )
    # zero kwh case
    assert (
        pytest.approx(calculate_electricity_costs(0, 1.5, 0.1, 100, 0.9125), 0.01)
        == 100
    )
    
    # Test that gvmt support covers 90% of the costs
    assert (
        pytest.approx(calculate_electricity_costs(100, 1, 0, 0, 0), 0.01)
        == 10
    )


def test_scenario_analysis_electricity_costs():
    kwh_usage_range = np.array([500, 1000])
    kwh_price_range = np.array([1.0, 1.5])
    result = scenario_analysis_electricity_costs(
        kwh_usage_range, kwh_price_range, 0.1, 100
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 4  # 2x2 combinations
    assert all(
        column in result.columns
        for column in ["kWh Usage", "kWh Price (NOK)", "Total Cost (NOK)"]
    )


def test_interest_rate_sensitivity():
    result = interest_rate_sensitivity(2500000, np.array([0.01, 0.02, 0.03]), 360)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert all(
        column in result.columns for column in ["Månedlig lånekostnad", "Rentesats"]
    )


def test_monthly_price_calculator():
    result = monthly_price_calculator(2500000, 0.03, 3000, 1500, 360)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert all(
        column in result.columns
        for column in ["lån_total", "rente", "elpris", "fk_hus", "total_beløp"]
    )


def test_monthly_price_calculator_scenarios():
    result = monthly_price_calculator_scenarios(
        [2000000, 2500000],
        [0.02, 0.03],
        [3000],
        [1000],
        [1.0],
        [0.1],
        [100],
        [360],
        [12000],
        [12000],
        [200000],
        [500000],
        [0.5],
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 4  # 2x2 combinations
    assert all(
        column in result.columns
        for column in [
            "house_price",
            "interest_rate",
            "monthly_loan_payment",
            "a_total",
            "b_total",
        ]
    )


if __name__ == "__main__":
    pytest.main()

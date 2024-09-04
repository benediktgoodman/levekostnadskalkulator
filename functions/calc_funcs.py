# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 2024

@author: Benedikt Goodman
"""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd
import numpy as np
import numpy_financial as npf

from itertools import product


def calculate_amortization_schedule(
    loan_amount: float, annual_interest_rate: float, loan_term_months: int
):
    """Calculate the amortization schedule for a loan.

    Parameters
    ----------
    loan_amount : float
        The total amount of the loan.
    annual_interest_rate : float
        The annual interest rate of the loan.
    loan_term_months : int
        The number of months the loan will be amortized over.

    Returns
    -------
    pd.DataFrame
        A dataframe containing the amortization schedule, with the following columns:
        - Month: The current month of the loan term.
        - Payment: The monthly payment amount.
        - Principal: The amount of the monthly payment that goes towards the principal.
        - Interest: The amount of the monthly payment that goes towards interest.
        - Remaining Balance: The remaining balance of the loan after the current month's payment.

    Examples
    --------
    >>> calculate_amortization_schedule(100000, 0.05, 360)
       Month   Payment  Principal  Interest  Remaining Balance
    0      1  536.8820  133.3333   403.5487          99866.6667
    1      2  536.8820  133.7734   403.1086          99732.8933
    2      3  536.8820  134.2146   402.6674          99598.6787
    ...
    """
    monthly_rate = annual_interest_rate / 12
    monthly_payment = npf.pmt(monthly_rate, loan_term_months, -loan_amount)

    remaining_balance = np.full(loan_term_months, loan_amount)
    interest_payment = remaining_balance * monthly_rate
    principal_payment = monthly_payment - interest_payment
    remaining_balance = np.cumsum(remaining_balance - principal_payment)

    schedule = pd.DataFrame({
        "Month": np.arange(1, loan_term_months + 1),
        "Payment": monthly_payment,
        "Principal": principal_payment,
        "Interest": interest_payment,
        "Remaining Balance": remaining_balance,
    })

    return schedule


def calculate_govt_support(
    kwh_usage: int | float,
    kwh_price_incl_vat_nok: int | float,
    govt_support_limit_nok: float = 0.9125,
):
    """
    Calculate the government support for electricity usage based on usage, price, and the support limit.

    Parameters
    ----------
    kwh_usage : float
        The electricity usage in kWh.
    kwh_price_incl_vat_nok : float
        The price of electricity per kWh, including VAT, in Norwegian Kroner (NOK).
    govt_support_limit_nok : float
        The government support limit price per kWh in Norwegian Kroner (NOK).

    Returns
    -------
    float
        The calculated government support amount in Norwegian Kroner (NOK).

    Examples
    --------
    >>> calculate_govt_support(100, 1.5, 0.9125)
    4.725
    """
    if kwh_usage <= 5000:
        govt_support = (
            kwh_usage * (kwh_price_incl_vat_nok - govt_support_limit_nok)
        ) * 0.9
    else:
        govt_support = 0
    return govt_support


def calculate_electricity_costs(
    kwh_usage: int,
    kwh_price_incl_vat_nok: int | float,
    markup_nok: int | float,
    fixed_cost_nok: float | int,
    govt_support_limit_nok: float = 0.9125,
):
    """
    Calculate the total cost of electricity usage, including fixed costs and government support.

    Parameters
    ----------
    kwh_usage : int | float
        The amount of electricity usage in kilowatt-hours (kWh).
    kwh_price_incl_vat_nok : int | float
        The price of electricity per kWh, including value-added tax (VAT) in Norwegian kroner (NOK).
    markup_nok : int | float
        The additional markup cost per kWh in NOK.
    fixed_cost_nok : int | float
        The fixed cost of electricity in NOK.
    govt_support_limit_nok : float, optional
        The government support limit price per kWh in NOK, by default 0.9125.

    Returns
    -------
    float
        The total cost of electricity usage in NOK.

    Examples
    --------
    >>> calculate_electricity_costs(1000, 1.2, 0.1, 100)
    1410.0
    >>> calculate_electricity_costs(1000, 1.5, 0.1, 100)
    1592.5
    """
    # Calculates cost without any govt support
    costs = fixed_cost_nok + (kwh_usage * (kwh_price_incl_vat_nok + markup_nok))

    if kwh_price_incl_vat_nok <= govt_support_limit_nok:
        return costs

    # Calculates amount of support, which is 0.9 times the difference between the support limit
    # and price
    govt_support_amount = calculate_govt_support(
        kwh_usage, kwh_price_incl_vat_nok, govt_support_limit_nok
    )

    return costs - govt_support_amount


def scenario_analysis_electricity_costs(
    kwh_usage_range: np.ndarray,
    kwh_price_range: np.ndarray,
    markup_nok: float,
    fixed_cost_nok: float,
    govt_support_limit_nok: float = 0.9125,
) -> pd.DataFrame:
    """
    Generate scenarios for different electricity usages and prices, calculating the total cost for each.

    Parameters
    ----------
    kwh_usage_range : np.ndarray
        Range of kilowatt-hours (kWh) usages to analyze.
    kwh_price_range : np.ndarray
        Range of prices per kWh in NOK to analyze.
    markup_nok : float
        The additional markup cost per kWh in NOK.
    fixed_cost_nok : float
        The fixed cost of electricity in NOK.
    govt_support_limit_nok : float, optional
        The government support limit price per kWh in NOK.

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns for kWh usage, kWh price, and the total cost of electricity.
    """
    # Prepare the result list
    scenarios = []

    # Iterate over all combinations of kWh usage and kWh price
    for kwh_usage in kwh_usage_range:
        for kwh_price in kwh_price_range:
            # Calculate total cost using the function
            total_cost = calculate_electricity_costs(
                kwh_usage, kwh_price, markup_nok, fixed_cost_nok, govt_support_limit_nok
            )
            # Append each scenario's result to the list
            scenarios.append(
                {
                    "kWh Usage": kwh_usage,
                    "kWh Price (NOK)": kwh_price,
                    "Total Cost (NOK)": total_cost,
                }
            )

    # Convert the list of dictionaries to a DataFrame for easier analysis and visualization
    return pd.DataFrame(scenarios)


# @validate_call(config=dict(arbitrary_types_allowed=True))
def loan_calc(
    loan: int | float, rate: float | np.ndarray, months: int
) -> int | np.ndarray:
    """
    Calculate the monthly payment for a given loan amount with a given interest rate over a specified number of months.

    Parameters
    ----------
    loan : float
        The loan amount.
    rate : float
        The annual interest rate.
    months : int
        The number of months over which the loan will be amortized.

    Returns
    -------
    float or np.ndarray
        The monthly payment.

    Examples
    --------
    >>> loan_calc(100000, 0.035, 360)
    448.64
    """
    return (rate / 12) * (1 / (1 - (1 + rate / 12) ** (-months))) * loan


# @validate_call(config=dict(arbitrary_types_allowed=True))
def interest_rate_sensitivity(
    houseprice_nok: int, interest_rate_range: np.ndarray, ammortisation_periods: int
) -> pd.DataFrame:
    """
    Calculate the monthly loan cost for a range of interest rates and amortization periods.

    Parameters
    ----------
    houseprice_nok : int
        The price of the house in Norwegian kroner (NOK).
    interest_rate_range : np.ndarray
        A numpy ndarray of interest rates to calculate the monthly loan cost for.
    ammortisation_periods : int
        The number of amortization periods (typically in months).

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the monthly loan cost and corresponding interest rate.

    Examples
    --------
    >>> interest_rate_range = np.arange(0.01, 0.06, 0.01)
    >>> interest_rate_sensitivity(2500000, interest_rate_range, 360)
       Månedlig lånekostnad  Rentesats
    0             8982.0        0.01
    1            10210.0        0.02
    2            11439.0        0.03
    3            12667.0        0.04
    4            13896.0        0.05
    """
    df = pd.DataFrame()
    # Calculates monthly loan calc function in listcomp, then turns it into a pandas series
    df["Månedlig lånekostnad"] = pd.Series(
        loan_calc(houseprice_nok, interest_rate_range, ammortisation_periods)
    ).round(0)
    df["Rentesats"] = pd.Series(interest_rate_range)

    return df


def monthly_price_calculator(
    houseprice: float,
    interest_rate: float,
    fixed_cost_house: float,
    elprice: float,
    ammortisation_periods: int,
    person_a_fixed_costs: float = 12349,
    person_b_fixed_costs: float = 12000,
    transaction_costs: float = 200000,
    ek: float = 2280000,
    ownership_fraq: float = 0.33,
    max_loan_limit: float = None,
) -> pd.DataFrame:
    """
    Calculate the monthly cost of owning a house for two people, given the house price, interest rate, fixed costs,
    electricity price, amortization periods, and other optional parameters.

    The function assumes a 50/50 split in electricity costs between person_a and person_b.

    Parameters
    ----------
    houseprice : float
        The price of the house.
    interest_rate : float
        The annual interest rate.
    fixed_cost_house : float
        Fixed costs of house, should include OBOS-fee etc.
    elprice : float
        The price of electricity.
    ammortisation_periods : int
        The number of months over which the loan will be amortized.
    person_a_fixed_costs : float, optional
        The fixed costs of person A, by default 12349.
    person_b_fixed_costs : float, optional
        The fixed costs of person B, by default 12000.
    transaction_costs : float, optional
        The costs associated with the transaction, by default 200000.
    ek : float, optional
        The value of the house, by default 2280000.
    ownership_fraq : float, optional
        The fraction of ownership for person A, by default 0.33.
    max_loan_limit : float, optional
        The maximum loan limit, by default None.

    Returns
    -------
    pd.DataFrame
        A dataframe containing the monthly costs for person A and person B.

    Examples
    --------
    >>> monthly_price_calculator(2500000, 0.015, 3000, 1500, 360)
           lån_total  rente  elprice  fk_hus  total_beløp  a_beløp_hus  b_beløp_hus  a_total  b_total
    0  8877.280741  0.015    1500    3000      13377.28  4611.640371  5674.860370  16951.64  17674.86
    """

    # Antar eierfraksjon basert på excel data
    rest_fraq = 1 - ownership_fraq

    # trekk fra omkostninger ved boligkjøp
    eff_ek = ek - transaction_costs

    # Lokale konstanter for lånsbalanse
    loan = houseprice - eff_ek

    if max_loan_limit:
        if loan > max_loan_limit:
            msg = [
                "Maksimalt lånebeløp oversteget.",
                f"Maks lån tillatt er {max_loan_limit}.",
                f"Beregnet lån med input er {loan}",
            ]
            return print(" ".join(msg))

    # Få månedlige lånekostnader
    monthly_loan = pd.Series(loan_calc(loan, interest_rate, ammortisation_periods))

    # Sammenstill dataframe
    df = pd.DataFrame(monthly_loan, columns=["lån_total"]).assign(
        rente=interest_rate, elpris=elprice
    )

    # Regn ut totalbeløp på lån + elpris og felleskosnader
    df["fk_hus"] = fixed_cost_house
    df["total_beløp"] = df["lån_total"] + df["elpris"] + df["fk_hus"]
    df["a_beløp_hus"] = (
        (df["lån_total"] * ownership_fraq) + (df["elpris"] / 2) + (df["fk_hus"] / 2)
    )
    df["b_beløp_hus"] = (
        (df["lån_total"] * rest_fraq) + (df["elpris"] / 2) + (df["fk_hus"] / 2)
    )

    # Legg til faste månedlige kostnader
    df["a_total"] = df["a_beløp_hus"] + person_a_fixed_costs
    df["b_total"] = df["b_beløp_hus"] + person_b_fixed_costs

    df["person_a_eierandel"] = ownership_fraq
    df["person_b_eierandel"] = rest_fraq

    return df


def monthly_price_calculator_scenarios(
    houseprice_range: list,
    interest_rate_range: list,
    fixed_cost_house_range: list,
    kwh_usage_range: list,
    kwh_price_range: list,
    markup_nok_range: list,
    fixed_cost_electricity_range: list,
    ammortisation_periods_range: list,
    person_a_fixed_costs_range: list,
    person_b_fixed_costs_range: list,
    transaction_costs_range: list,
    ek_range: list,
    ownership_fraq_range: list,
):
    """
    Generate scenarios for varying parameters of house ownership costs.

    Parameters
    ----------
    houseprice_range : list
        Range of house prices to analyze.
    interest_rate_range : list
        Range of interest rates to analyze.
    fixed_cost_house_range : list
        Range of fixed costs for house to analyze.
    kwh_usage_range : list
        Range of electricity usages (kWh) to analyze.
    kwh_price_range : list
        Range of electricity prices (NOK per kWh) to analyze.
    markup_nok_range : list
        Range of additional markup costs per kWh in NOK to analyze.
    fixed_cost_electricity_range : list
        Range of fixed costs for electricity in NOK to analyze.
    ammortisation_periods_range : list
        Range of amortisation periods (months) to analyze.
    person_a_fixed_costs_range : list
        Range of fixed costs for person A to analyze.
    person_b_fixed_costs_range : list
        Range of fixed costs for person B to analyze.
    transaction_costs_range : list
        Range of transaction costs to analyze.
    ek_range : list
        Range of equity amounts to analyze.
    ownership_fraq_range : list
        Range of ownership fractions to analyze.
    govt_support_limit_nok_range : list
        Range of government support limit prices per kWh in NOK to analyze.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing all the scenarios and their respective calculations.
    """
    # Generate all combinations of input parameters
    all_combinations = list(
        product(
            houseprice_range,
            interest_rate_range,
            fixed_cost_house_range,
            kwh_usage_range,
            kwh_price_range,
            markup_nok_range,
            fixed_cost_electricity_range,
            ammortisation_periods_range,
            person_a_fixed_costs_range,
            person_b_fixed_costs_range,
            transaction_costs_range,
            ek_range,
            ownership_fraq_range,
        )
    )

    results = []

    # Process each combination of parameters
    for (
        house_price,
        interest_rate,
        fixed_cost_house,
        kwh_usage,
        kwh_price,
        markup_nok,
        fixed_cost_electricity,
        ammortisation_periods,
        person_a_fixed_costs,
        person_b_fixed_costs,
        transaction_costs,
        ek,
        ownership_fraq,
    ) in all_combinations:
        # Calculate effective equity after transaction costs
        eff_ek = ek - transaction_costs
        # Calculate loan amount
        loan = house_price - eff_ek

        # Calculate monthly loan payment using loan_calc function
        monthly_loan_payment = loan_calc(loan, interest_rate, ammortisation_periods)

        # Calculate electricity costs using calculate_electricity_costs function
        el_cost = calculate_electricity_costs(
            kwh_usage, kwh_price, markup_nok, fixed_cost_electricity
        )

        # Calculate ownership shares
        a_share = (
            (monthly_loan_payment * ownership_fraq)
            + (el_cost / 2)
            + (fixed_cost_house / 2)
        )
        b_share = (
            (monthly_loan_payment * (1 - ownership_fraq))
            + (el_cost / 2)
            + (fixed_cost_house / 2)
        )

        # Sum up total costs per person
        a_total = a_share + person_a_fixed_costs
        b_total = b_share + person_b_fixed_costs

        # Append the results to the list
        results.append(
            {
                "house_price": house_price,
                "interest_rate": interest_rate,
                "fixed_cost_house": fixed_cost_house,
                "kwh_usage": kwh_usage,
                "kwh_price": kwh_price,
                "markup_nok": markup_nok,
                "fixed_cost_electricity": fixed_cost_electricity,
                "el_cost": el_cost,
                "ammortisation_periods": ammortisation_periods,
                "person_a_fixed_costs": person_a_fixed_costs,
                "person_b_fixed_costs": person_b_fixed_costs,
                "transaction_costs": transaction_costs,
                "ek": ek,
                "ownership_fraq": ownership_fraq,
                "monthly_loan_payment": monthly_loan_payment,
                "a_total": a_total,
                "b_total": b_total,
            }
        )

    # Convert the list of dictionaries to a DataFrame
    results_df = pd.DataFrame(results)
    return results_df

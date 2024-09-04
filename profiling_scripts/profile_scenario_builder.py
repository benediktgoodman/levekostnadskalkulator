import cProfile
import pstats
import io
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from functions.calc_funcs import (
    monthly_price_calculator_scenarios,
    calculate_amortization_schedule
)
from functions.plot_funcs import (
    create_cost_breakdown_sunburst,
    create_interest_rate_sensitivity_chart,
    create_amortization_chart
)
from classes.state_manager import ScenarioState

def run_initial_scenario():
    # Sample input data
    houseprice_range = (3000000, 5000000)
    interest_rates_decimal = np.arange(0.01, 0.06, 0.0025)
    fixed_cost_house = 5000
    kwh_usage_range = 500
    kwh_price_range = 1.5
    markup_nok = 0.1
    fixed_cost_electricity = 39
    ammortisation_periods = 360
    person_a_fixed_costs = 10000
    person_b_fixed_costs = 10000
    transaction_costs = 200000
    ek = 1500000
    ownership_fraq = 50

    # Calculate scenarios
    df = monthly_price_calculator_scenarios(
        houseprice_range=np.arange(*houseprice_range, step=100000),
        interest_rate_range=interest_rates_decimal,
        fixed_cost_house_range=[fixed_cost_house],
        kwh_usage_range=[kwh_usage_range],
        kwh_price_range=[kwh_price_range],
        markup_nok_range=[markup_nok],
        fixed_cost_electricity_range=[fixed_cost_electricity],
        ammortisation_periods_range=[ammortisation_periods],
        person_a_fixed_costs_range=[person_a_fixed_costs],
        person_b_fixed_costs_range=[person_b_fixed_costs],
        transaction_costs_range=[transaction_costs],
        ek_range=[ek],
        ownership_fraq_range=[ownership_fraq / 100]
    )

    # Initialize ScenarioState
    state = ScenarioState()
    state.df = df
    state.selected_house_price = df["house_price"].unique()[0]
    state.selected_interest_rate = df["interest_rate"].unique()[0]

    # Filter data and update state
    filtered_df = state.df[
        (state.df["house_price"] == state.selected_house_price)
        & (state.df["interest_rate"] == state.selected_interest_rate)
    ]
    state.update(filtered_df, state.selected_house_price, ek, ammortisation_periods)

    # Generate initial charts
    create_cost_breakdown_sunburst(state.df, 'A')
    create_cost_breakdown_sunburst(state.df, 'B')
    create_interest_rate_sensitivity_chart(state.loan_amount_a, ammortisation_periods, interest_rates_decimal)
    create_interest_rate_sensitivity_chart(state.loan_amount_b, ammortisation_periods, interest_rates_decimal)
    create_amortization_chart(state.schedule_a, "Person A")
    create_amortization_chart(state.schedule_b, "Person B")

    return state, ek, ammortisation_periods

def simulate_user_interaction(state, ek, ammortisation_periods):
    # Simulate changing house price
    state.selected_house_price = state.df["house_price"].unique()[1]  # Select second house price

    # Simulate changing interest rate
    state.selected_interest_rate = state.df["interest_rate"].unique()[1]  # Select second interest rate
    
    # Re-filter data and update state
    filtered_df = state.df[
        (state.df["house_price"] == state.selected_house_price)
        & (state.df["interest_rate"] == state.selected_interest_rate)
    ]
    state.update(filtered_df, state.selected_house_price, ek, ammortisation_periods)

    # Regenerate charts
    create_cost_breakdown_sunburst(state.df, 'A')
    create_cost_breakdown_sunburst(state.df, 'B')
    create_interest_rate_sensitivity_chart(state.loan_amount_a, ammortisation_periods, state.df["interest_rate"].unique())
    create_interest_rate_sensitivity_chart(state.loan_amount_b, ammortisation_periods, state.df["interest_rate"].unique())
    create_amortization_chart(state.schedule_a, "Person A")
    create_amortization_chart(state.schedule_b, "Person B")

def profile_scenario_builder():
    # Profile the initial scenario setup
    initial_profiler = cProfile.Profile()
    initial_profiler.enable()
    state, ek, ammortisation_periods = run_initial_scenario()
    initial_profiler.disable()
    
    print("Profiling results for initial scenario setup:")
    s = io.StringIO()
    ps = pstats.Stats(initial_profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(30)  # Print top 30 time-consuming functions
    print(s.getvalue())

    # Profile the user interaction simulation
    interaction_profiler = cProfile.Profile()
    interaction_profiler.enable()
    simulate_user_interaction(state, ek, ammortisation_periods)
    interaction_profiler.disable()
    
    print("\nProfiling results for user interaction simulation:")
    s = io.StringIO()
    ps = pstats.Stats(interaction_profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(30)  # Print top 30 time-consuming functions
    print(s.getvalue())

if __name__ == "__main__":
    profile_scenario_builder()
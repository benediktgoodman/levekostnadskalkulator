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

from functions.plot_funcs import (
    create_cost_breakdown_sunburst,
    create_interest_rate_sensitivity_chart,
    create_amortization_chart
)
from functions.calc_funcs import (
    monthly_price_calculator_scenarios,
    calculate_amortization_schedule
)

interest_rate_rage = np.arange(0.01, 0.1, 0.0025)

def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(30)  # Print top 30 time-consuming functions
    
    print(f"Profiling results for {func.__name__}:")
    print(s.getvalue())
    
    return result

def create_sample_data():
    # Use monthly_price_calculator_scenarios to generate realistic data
    sunburst_data = monthly_price_calculator_scenarios(
        houseprice_range=[5000000],
        interest_rate_range=[0.06],
        fixed_cost_house_range=[5000],
        kwh_usage_range=[500],
        kwh_price_range=[1.5],
        markup_nok_range=[0.1],
        fixed_cost_electricity_range=[39],
        ammortisation_periods_range=[360],
        person_a_fixed_costs_range=[10000],
        person_b_fixed_costs_range=[10000],
        transaction_costs_range=[200000],
        ek_range=[1500000],
        ownership_fraq_range=[0.5]
    )
    
    # # Sample row for sunburst chart
    # sunburst_data = df.iloc[0]
    
    # # Prepare data for cost breakdown sunburst
    # sunburst_data = pd.DataFrame({
    #     'kategori': ['Boligkostnader', 'Boligkostnader', 'Boligkostnader', 'Personlige kostnader'],
    #     'underkategori': ['Lånebetaling', 'Faste boligkostnader', 'Strøm', 'Andre faste kostnader'],
    #     'verdi': [
    #         sample_row['monthly_loan_payment'] * sample_row['ownership_fraq'],
    #         sample_row['fixed_cost_house'] / 2,
    #         sample_row['el_cost'] / 2,
    #         sample_row['person_a_fixed_costs']
    #     ]
    # })
    
    # Data for interest rate sensitivity chart
    loan_amount = sunburst_data['house_price'] - 1500000  # Assuming ek is 1500000
    amortization_periods = 360
    interest_rate_range = sunburst_data['interest_rate'].unique()
    
    # Data for amortization chart
    amortization_schedule = calculate_amortization_schedule(
        loan_amount, 
        sunburst_data['interest_rate'], 
        amortization_periods
    )
    
    return sunburst_data, loan_amount, amortization_periods, interest_rate_range, amortization_schedule

def main():
    sunburst_data, loan_amount, amortization_periods, interest_rate_range, amortization_schedule = create_sample_data()
    
    # Profile create_cost_breakdown_sunburst
    profile_function(create_cost_breakdown_sunburst, sunburst_data, 'A')
    
    # Profile create_interest_rate_sensitivity_chart
    profile_function(create_interest_rate_sensitivity_chart, loan_amount, amortization_periods, (0.01, 0.1))
    
    # Profile create_amortization_chart
    profile_function(create_amortization_chart, amortization_schedule, "Person A")

if __name__ == "__main__":
    main()
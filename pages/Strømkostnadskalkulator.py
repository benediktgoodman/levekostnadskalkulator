import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path
import os

# Find root folder in project
script_path = Path(os.getcwd())
while "Boligkostnadskalkulatoren.py" not in os.listdir():
    os.chdir("../")

from functions.calc_functions import scenario_analysis_electricity_costs
from functions.plot_figures import create_heatmap_divergent_hover
from functions.metric_cards import electricity_metric_cards
from functions import input_logic_funcs

os.chdir(script_path)

@st.cache_data
def calculate_electricity_costs(kwh_usage_range, kwh_price_range, markup_nok, fixed_cost_nok):
    return scenario_analysis_electricity_costs(
        kwh_usage_range=np.linspace(kwh_usage_range[0], kwh_usage_range[1], 50),
        kwh_price_range=np.linspace(kwh_price_range[0], kwh_price_range[1], 50),
        markup_nok=markup_nok,
        fixed_cost_nok=fixed_cost_nok,
    )

def main():
    st.set_page_config(layout='centered')
    st.title("Beregning av månedlige strømkostnader")
        
    st.write("""
    Denne kalkulatoren hjelper deg med å estimere dine månedlige strømkostnader basert på forbruk og priser. 
    Modellen inkluderer den norske strømstøtteordningen.

    Bruk sliderne nedenfor for å utforske hvordan ulike forbruksnivåer og priser påvirker din totale strømkostnad.
    """)

    kwh_usage_range = st.slider(
        "Velg intervall for strømforbruk (kWh):",
        min_value=100,
        max_value=5000,
        value=(300, 700),
        step=100,
    )
    kwh_usage_range = input_logic_funcs.ensure_range(kwh_usage_range, 100, 5000, 100)
    
    kwh_price_range = st.slider(
        "Velg intervall for spotpris (kr/kWh):",
        min_value=0.1,
        max_value=10.0,
        value=(1.0, 2.0),
        step=0.1,
    )
    kwh_price_range = input_logic_funcs.ensure_range(kwh_price_range, 0.1, 10.0, 0.1)
    
    markup_nok = st.number_input("Påslag per kWh (kr):", value=0.1, min_value=0.0, max_value=1.0, step=0.01)
    fixed_cost_nok = st.number_input("Fastprisledd (kr):", value=39, min_value=0, max_value=500, step=1)

    df = calculate_electricity_costs(kwh_usage_range, kwh_price_range, markup_nok, fixed_cost_nok)

    st.subheader("Oppsummert kostnadsbilde")
    electricity_metric_cards(df)
    
    st.plotly_chart(create_heatmap_divergent_hover(
        df, 
        x_column='kWh Price (NOK)', 
        y_column='kWh Usage', 
        z_column='Total Cost (NOK)',
        title='Strømkostnader',
        x_axis_title='Pris per kWh (NOK)',
        y_axis_title='Strømforbruk (kWh)',
        colorbar_title='Totalkostnad (NOK)'
    ), use_container_width=True)

    st.write("""
    **Om strømstøtteordningen**
    - Staten dekker 90% av strømprisen som overstiger 70 øre per kWh.
    - Støtten beregnes time for time og er basert på spotprisen i ditt prisområde.
    - Ordningen gjelder for forbruk opp til 5000 kWh per måned.
    - Støtten trekkes automatisk fra på strømregningen din.
    """)

if __name__ == "__main__":
    main()
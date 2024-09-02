import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path
import os
import toml

# Find root folder in project
script_path = Path(os.getcwd())
while "Boligkostnadskalkulatoren.py" not in os.listdir():
    os.chdir("../")

from functions.calc_functions import scenario_analysis_electricity_costs
from functions.plot_figures import create_heatmap_divergent_hover
from functions.metric_cards import electricity_metric_cards
from functions import input_logic_funcs

os.chdir(script_path)

# Load constants from constants.toml
variables = toml.load("variables.toml")['electricity']

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
    Klikk på "Beregn kostnader" når du er klar til å se resultatene.
    """)

    kwh_usage_range = st.slider(
        variables["KWH_USAGE_RANGE_LABEL"],
        min_value=variables["KWH_USAGE_RANGE_MIN"],
        max_value=variables["KWH_USAGE_RANGE_MAX"],
        value=tuple(variables["KWH_USAGE_RANGE_DEFAULT"]),
        step=variables["KWH_USAGE_RANGE_STEP"],
    )
    kwh_usage_range = input_logic_funcs.ensure_range(kwh_usage_range, variables["KWH_USAGE_RANGE_MIN"], variables["KWH_USAGE_RANGE_MAX"], variables["KWH_USAGE_RANGE_STEP"])
    
    kwh_price_range = st.slider(
        variables["KWH_PRICE_RANGE_LABEL"],
        min_value=variables["KWH_PRICE_RANGE_MIN"],
        max_value=variables["KWH_PRICE_RANGE_MAX"],
        value=tuple(variables["KWH_PRICE_RANGE_DEFAULT"]),
        step=variables["KWH_PRICE_RANGE_STEP"],
    )
    kwh_price_range = input_logic_funcs.ensure_range(kwh_price_range, variables["KWH_PRICE_RANGE_MIN"], variables["KWH_PRICE_RANGE_MAX"], variables["KWH_PRICE_RANGE_STEP"])
    
    markup_nok = st.number_input(
        variables["MARKUP_NOK_LABEL"], 
        value=variables["MARKUP_NOK_DEFAULT"], 
        min_value=variables["MARKUP_NOK_MIN"], 
        max_value=variables["MARKUP_NOK_MAX"], 
        step=variables["MARKUP_NOK_STEP"]
    )
    fixed_cost_nok = st.number_input(
        variables["FIXED_COST_ELECTRICITY_LABEL"], 
        value=variables["FIXED_COST_ELECTRICITY_DEFAULT"], 
        min_value=variables["FIXED_COST_ELECTRICITY_MIN"], 
        max_value=variables["FIXED_COST_ELECTRICITY_MAX"], 
        step=variables["FIXED_COST_ELECTRICITY_STEP"]
    )

    # Add a button to trigger the calculation
    if st.button('Beregn kostnader'):
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
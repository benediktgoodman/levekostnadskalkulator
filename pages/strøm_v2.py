import streamlit as st
import numpy as np
import pandas as pd
import os
from pathlib import Path

# Finn rotmappe i prosjekt
script_path = Path(os.getcwd())

while "app.py" not in os.listdir():
    os.chdir("../")

from functions.calc_functions import scenario_analysis_electricity_costs  # noqa: E402
from functions.plot_figures import ( # noqa: E402
    create_heatmap_divergent_hover,
    ) 
from functions.metric_cards import electricity_metric_cards # noqa: E402
from functions import input_logic_funcs # noqa: E402

os.chdir(script_path)

def calculate_and_update(kwh_usage_range, kwh_price_range, markup_nok, fixed_cost_nok):
    df = scenario_analysis_electricity_costs(
        kwh_usage_range=np.linspace(kwh_usage_range[0], kwh_usage_range[1], 50),
        kwh_price_range=np.linspace(kwh_price_range[0], kwh_price_range[1], 50),
        markup_nok=markup_nok,
        fixed_cost_nok=fixed_cost_nok,
    )
    return df

def main():
    st.title("Beregning av månedlige strømkostnader")
        
    # Expanded explanation
    st.write("""
    Denne kalkulatoren hjelper deg med å estimere dine månedlige strømkostnader basert på forbruk og priser. 
    Modellen inkluderer den norske strømstøtteordningen.

    Bruk sliderne nedenfor for å utforske hvordan ulike forbruksnivåer og priser påvirker din totale strømkostnad.
    """)


    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
        st.session_state.calculated = False

    # Inputs for the scenario analysis
    kwh_usage_range = st.slider(
        "Velg intervall for strømforbruk (kWh):",
        min_value=100,
        max_value=5000,
        value=(300, 700),
        step=100,
        key='kwh_usage_range'
    )
    kwh_usage_range = input_logic_funcs.ensure_range(kwh_usage_range, 100, 5000, 100)
    
    kwh_price_range = st.slider(
        "Velg intervall for spotpris (kr/kWh):",
        min_value=0.2,
        max_value=5.0,
        value=(1.0, 2.0),
        step=0.1,
        key='kwh_price_range'
    )
    kwh_price_range = input_logic_funcs.ensure_range(kwh_price_range, 0.2, 5.0, 0.1)
    
    markup_nok = st.number_input("Påslag per kWh (kr):", value=0.1, key='markup_nok')
    fixed_cost_nok = st.number_input("Fastprisledd (kr):", value=39, key='fixed_cost_nok')

    # Button to initialize calculation
    if not st.session_state.calculated:
        if st.button("Beregn kostnader"):
            st.session_state.df = calculate_and_update(kwh_usage_range, kwh_price_range, markup_nok, fixed_cost_nok)
            st.session_state.calculated = True
    
    # Auto-update when inputs change
    if st.session_state.calculated:
        st.session_state.df = calculate_and_update(kwh_usage_range, kwh_price_range, markup_nok, fixed_cost_nok,)

        # Display summary statistics
        st.subheader("Oppsummert kostnadsbilde")
        electricity_metric_cards(st.session_state.df)
        
        # Display heatmap
        st.plotly_chart(create_heatmap_divergent_hover(
            st.session_state.df, 
            x_column='kWh Price (NOK)', 
            y_column='kWh Usage', 
            z_column='Total Cost (NOK)',
            title='Strømkostnader',
            x_axis_title='Pris per kWh (NOK)',
            y_axis_title='Strømforbruk (kWh)',
            colorbar_title='Totalkostnad (NOK)'
        ))

        st.write("""
        **Om strømstøtteordningen**
        - Staten dekker 90% av strømprisen som overstiger 70 øre per kWh.
        - Støtten beregnes time for time og er basert på spotprisen i ditt prisområde.
        - Ordningen gjelder for forbruk opp til 5000 kWh per måned.
        - Støtten trekkes automatisk fra på strømregningen din.
        """)
        
        # # Display data table
        # st.subheader("Detaljert data")
        # st.dataframe(st.session_state.df.style.format({"Total Cost (NOK)": "kr{:.2f}", "kWh Price (NOK)": "kr{:.2f}"}))

if __name__ == "__main__":
    main()
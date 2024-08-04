import streamlit as st
import os
from pathlib import Path
import toml
import numpy as np
import pandas as pd

# Finn rotmappe i prosjekt
script_path = Path(os.getcwd())

while "app.py" not in os.listdir():
    os.chdir("../")

from functions.calc_functions import (
    monthly_price_calculator_scenarios
)

# Load constants from constants.toml
variables = toml.load("variables.toml")['constants']

# Change working dir back to script
os.chdir(script_path)

def main():
    st.set_page_config(layout='centered')
    st.title(variables["APP_TITLE"])
    
    # Ownership splitting
    with st.container():
        st.subheader('Eierskap')
        ownership_fraq = st.slider(variables["OWNERSHIP_FRAQ_SLIDER_LABEL"],
                                   min_value=variables["OWNERSHIP_FRAQ_MIN"], max_value=variables["OWNERSHIP_FRAQ_MAX"], value=variables["OWNERSHIP_FRAQ_DEFAULT"])
        
        # Calculate ownership for person A and person B
        person_a_ownership = ownership_fraq
        person_b_ownership = 100 - ownership_fraq

        # Display ownership fractions
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Person A:", value=f'{person_a_ownership}%')
            st.progress(person_a_ownership / 100)
        with col2:
            st.metric(label='Person B:', value=f'{person_b_ownership}%')
            st.progress(person_b_ownership / 100)
    
    # Housing Loan
    with st.container():
        st.subheader('Boliglån')
        # Cache numerical function
        monthly_price_calculator_scenarios_cached = st.cache_data(monthly_price_calculator_scenarios)

        # House price inputs
        houseprice_range = st.slider(variables["HOUSEPRICE_SLIDER_LABEL"],
                                     min_value=variables["HOUSEPRICE_MIN"], max_value=variables["HOUSEPRICE_MAX"], value=tuple(variables["HOUSEPRICE_DEFAULT"]), step=variables["HOUSEPRICE_STEP"])
        
        ammortisation_periods = st.number_input(variables["AMMORTISATION_PERIOD_LABEL"], min_value=variables["AMMORTISATION_PERIOD_MIN"], max_value=variables["AMMORTISATION_PERIOD_MAX"], value=variables["AMMORTISATION_PERIOD_DEFAULT"])
        ek = st.number_input(variables["EK_LABEL"], value=variables["EK_DEFAULT"], step=variables["EK_STEP"])
    
        interest_rate_range = st.slider(variables["INTEREST_RATE_SLIDER_LABEL"],
                                        min_value=variables["INTEREST_RATE_MIN"], max_value=variables["INTEREST_RATE_MAX"], value=tuple(variables["INTEREST_RATE_DEFAULT"]), step=variables["INTEREST_RATE_STEP"])
    
    # Monthly costs
    with st.container():
        st.subheader('Strøm')
        elprice_range = st.number_input(variables["ELPRICE_SLIDER_LABEL"],
                                  min_value=variables["ELPRICE_MIN"], max_value=variables["ELPRICE_MAX"], value=variables["ELPRICE_DEFAULT"])
    
    # Other fixed cost section
    with st.container():
        st.subheader('Faste kostnader')
        # Single-value inputs
        fixed_cost_house = st.number_input(variables["FIXED_COST_HOUSE_LABEL"], value=variables["FIXED_COST_HOUSE_DEFAULT"], step=variables["FIXED_COST_HOUSE_STEP"])
        
        person_a_fixed_costs = st.number_input(variables["PERSON_A_FIXED_COSTS_LABEL"], value=variables["PERSON_A_FIXED_COSTS_DEFAULT"], step=variables["PERSON_A_FIXED_COSTS_STEP"])
        person_b_fixed_costs = st.number_input(variables["PERSON_B_FIXED_COSTS_LABEL"], value=variables["PERSON_B_FIXED_COSTS_DEFAULT"], step=variables["PERSON_B_FIXED_COSTS_STEP"])
        transaction_costs = st.number_input(variables["TRANSACTION_COSTS_LABEL"], value=variables["TRANSACTION_COSTS_DEFAULT"], step=variables["TRANSACTION_COSTS_STEP"])

    # Convert interest rates from percentages to decimals
    interest_rates_decimal = np.arange(interest_rate_range[0] / 100, interest_rate_range[1] / 100 + 0.005, 0.005)

    if st.button("Beregn kostnader"):
        # Call the function to calculate scenarios
        df = monthly_price_calculator_scenarios_cached(
            houseprice_range=np.arange(*houseprice_range, step=100000),
            interest_rate_range=interest_rates_decimal,
            fixed_cost_house_range=[fixed_cost_house],  # Wrap single values in lists to comply with function signature
            elprice_range=[elprice_range],
            ammortisation_periods_range=[ammortisation_periods],
            person_a_fixed_costs_range=[person_a_fixed_costs],
            person_b_fixed_costs_range=[person_b_fixed_costs],
            transaction_costs_range=[transaction_costs],
            ek_range=[ek],
            ownership_fraq_range=[ownership_fraq]
        )
        
        #TODO: Find some way of plotting the results

if __name__ == "__main__":
    main()

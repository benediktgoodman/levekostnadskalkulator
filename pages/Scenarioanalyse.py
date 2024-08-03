import streamlit as st
import os
from pathlib import Path
import toml
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Finn rotmappe i prosjekt
script_path = Path(os.getcwd())

while "app.py" not in os.listdir():
    os.chdir("../")

from functions.calc_functions import monthly_price_calculator_scenarios

# Load constants from constants.toml
vars = toml.load("variables.toml")["constants"]

# Change working dir back to script
os.chdir(script_path)


def main():
    st.set_page_config(layout="centered")
    st.title(vars["APP_TITLE"])

    # Use tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Eierskap", "Boliglån", "Strøm", "Faste kostnader"]
    )

    with tab1:
        st.subheader("Eierskap")
        ownership_fraq = st.slider(
            vars["OWNERSHIP_FRAQ_SLIDER_LABEL"],
            min_value=vars["OWNERSHIP_FRAQ_MIN"],
            max_value=vars["OWNERSHIP_FRAQ_MAX"],
            value=vars["OWNERSHIP_FRAQ_DEFAULT"],
        )

        # Calculate ownership for person A and person B
        person_a_ownership = ownership_fraq
        person_b_ownership = 100 - ownership_fraq

        # Display ownership fractions
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Person A:", value=f"{person_a_ownership}%")
            st.progress(person_a_ownership / 100)
        with col2:
            st.metric(label="Person B:", value=f"{person_b_ownership}%")
            st.progress(person_b_ownership / 100)

    with tab2:
        st.subheader("Boliglån")
        # Cache numerical function
        monthly_price_calculator_scenarios_cached = st.cache_data(
            monthly_price_calculator_scenarios
        )

        # House price inputs
        houseprice_range = st.slider(
            vars["HOUSEPRICE_SLIDER_LABEL"],
            min_value=vars["HOUSEPRICE_MIN"],
            max_value=vars["HOUSEPRICE_MAX"],
            value=tuple(vars["HOUSEPRICE_DEFAULT"]),
            step=vars["HOUSEPRICE_STEP"],
        )

        ammortisation_periods = st.number_input(
            vars["AMMORTISATION_PERIOD_LABEL"],
            min_value=vars["AMMORTISATION_PERIOD_MIN"],
            max_value=vars["AMMORTISATION_PERIOD_MAX"],
            value=vars["AMMORTISATION_PERIOD_DEFAULT"],
        )
        ek = st.number_input(
            vars["EK_LABEL"], value=vars["EK_DEFAULT"], step=vars["EK_STEP"]
        )

        interest_rate_range = st.slider(
            vars["INTEREST_RATE_SLIDER_LABEL"],
            min_value=vars["INTEREST_RATE_MIN"],
            max_value=vars["INTEREST_RATE_MAX"],
            value=tuple(vars["INTEREST_RATE_DEFAULT"]),
            step=vars["INTEREST_RATE_STEP"],
        )

    with tab3:
        st.subheader("Strøm")

        kwh_price = st.number_input(
            vars["ELPRICE_SLIDER_LABEL"],
            value=vars["ELPRICE_DEFAULT"],
        )
        kwh_usage = st.number_input("Strømforbruk (kWh):", value=1000)
        el_markup = st.number_input("Påslag per kWh (kr):", value=0.1)
        el_fixed_cost = st.number_input("Fastprisledd (kr):", value=39)

    with tab4:
        st.subheader("Faste kostnader")
        # Single-value inputs
        fixed_cost_house = st.number_input(
            vars["FIXED_COST_HOUSE_LABEL"],
            value=vars["FIXED_COST_HOUSE_DEFAULT"],
            step=vars["FIXED_COST_HOUSE_STEP"],
        )

        person_a_fixed_costs = st.number_input(
            vars["PERSON_A_FIXED_COSTS_LABEL"],
            value=vars["PERSON_A_FIXED_COSTS_DEFAULT"],
            step=vars["PERSON_A_FIXED_COSTS_STEP"],
        )
        person_b_fixed_costs = st.number_input(
            vars["PERSON_B_FIXED_COSTS_LABEL"],
            value=vars["PERSON_B_FIXED_COSTS_DEFAULT"],
            step=vars["PERSON_B_FIXED_COSTS_STEP"],
        )
        transaction_costs = st.number_input(
            vars["TRANSACTION_COSTS_LABEL"],
            value=vars["TRANSACTION_COSTS_DEFAULT"],
            step=vars["TRANSACTION_COSTS_STEP"],
        )

    # Convert interest rates from percentages to decimals
    interest_rates_decimal = np.arange(
        interest_rate_range[0] / 100, interest_rate_range[1] / 100 + 0.005, 0.005
    )

    if st.button("Calculate Scenarios"):
        # Call the function to calculate scenarios
        df = monthly_price_calculator_scenarios_cached(
            houseprice_range = np.arange(*houseprice_range, step=100000),
            interest_rate_range = interest_rates_decimal,
            fixed_cost_house_range = [fixed_cost_house],
            kwh_usage_range = [kwh_usage],
            kwh_price_range = [kwh_price],
            markup_nok_range = [el_markup],
            fixed_cost_electricity_range = [el_fixed_cost],
            ammortisation_periods_range = [ammortisation_periods],
            person_a_fixed_costs_range = [person_a_fixed_costs],
            person_b_fixed_costs_range = [person_b_fixed_costs],
            transaction_costs_range = [transaction_costs],
            ek_range = [ek],
            ownership_fraq_range=np.arange(ownership_fraq, step=1),
        )

        # Visualize the data
        st.subheader("Visualization")

        df["total_cost"] = df["a_total"] + df["b_total"]
        # df = df.sort_values('total_cost')

        # Heatmap of total cost vs house price and interest rate
        cols = ["house_price", "interest_rate", "a_total", "b_total"]


if __name__ == "__main__":
    main()

import streamlit as st
import os
from pathlib import Path

import plotly.express as px


import numpy as np
import pandas as pd

# Finn rotmappe i prosjekt
script_path = Path(os.getcwd())

while "app.py" not in os.listdir():
    os.chdir("../")

from functions.calc_functions import scenario_analysis_electricity_costs

os.chdir(script_path)


def main():
    # Cache function
    cached_scenario_func = st.cache_data(scenario_analysis_electricity_costs)

    st.title("Beregning av månedlige strømkostnader")
    st.write("Denne beregningen inneholder bla bla.... strømstøtte")

    # Inputs for the scenario analysis
    kwh_usage_range = st.slider(
        "Velg intervall for strømforbruk (kWh):",
        min_value=100,
        max_value=5000,
        value=(300, 700),
        step=100,
    )
    kwh_price_range = st.slider(
        "Velg intervall for spotpris (kr/kWh):",
        min_value=0.2,
        max_value=5.0,
        value=(1.0, 2.0),
        step=0.1,
    )
    markup_nok = st.number_input("Påslag per kWh (kr):", value=0.1)
    fixed_cost_nok = st.number_input("Fastprisledd (kr):", value=39)

    if st.button("Beregn kostnader"):
        # Call the scenario analysis function
        df = scenario_analysis_electricity_costs(
            kwh_usage_range=np.arange(kwh_usage_range[0], kwh_usage_range[1], 1),
            kwh_price_range=np.arange(
                kwh_price_range[0] - 0.1, kwh_price_range[1] + 0.1, 0.1
            ),
            markup_nok=markup_nok,
            fixed_cost_nok=fixed_cost_nok,
        )

        # Define the formatting dictionary
        format_dict = {"Total Cost (NOK)": "kr{:,.2f}"}

        # Apply the formatting
        # df.style.format(format_dict)

        fig = px.area(
            df.round(1),
            x="kWh Usage",
            y="Total Cost (NOK)",
            labels={
                "kWh Usage": "Strømforbruk (kWh)",
                "Total Cost (NOK)": "kr/måned",
                "kWh Price (NOK)": "Strømpris (kr/kwh)",
            },
            color="kWh Price (NOK)",
            width=1200,
            height=600,
        ).update_layout(
            yaxis=dict(
                tickformat=".0f"  # transforms 6k -> 6000
            )
        )

        st.subheader("Månedlige strømkostnader")
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

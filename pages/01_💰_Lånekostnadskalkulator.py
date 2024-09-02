# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 2024

@author: Benedikt Goodman
"""

import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))


from functions.calc_funcs import (  # noqa: E402
    loan_calc,
    interest_rate_sensitivity,
)


st.set_page_config(layout="centered")
# Streamlit app layout
st.title("Hva vil lånet ditt egentlig koste deg i måneden?")
st.write("""
🏠💸 Forstå boliglånet ditt bedre!

📊 Se hvordan renten påvirker månedlige kostnader
🎢 Utforsk ulike rentescenarioer - fra lav til høy
💡 Få innsikt i hvordan økonomiske svingninger påvirker deg

Husk: Selv små renteendringer kan ha stor effekt på lommeboken din! 💰

""")

# Cache functions that should be used
loan_calc_cached = st.cache_data(loan_calc)  # noqa: F841
interest_rate_sensitivity_cached = st.cache_data(interest_rate_sensitivity)

# User inputs
houseprice_nok = st.number_input(
    "Hvor mye låner du?:", min_value=100000, value=2500000, step=100000
)
interest_rate_min = st.number_input(
    "Hva er minste rentesats? (%):", min_value=0.0, value=1.0, step=0.1, format="%.2f"
)
interest_rate_max = st.number_input(
    "Hva er største rentsats (%):", min_value=0.0, value=5.0, step=0.1, format="%.2f"
)
interest_rate_step = st.number_input(
    "Intervallbredde på renteendringer (%):",
    min_value=0.25,
    value=0.25,
    step=0.25,
    format="%.2f",
)
ammortisation_periods = st.number_input(
    "Hva er tilbakebetalingstiden på lånet? (i antall måneder):",
    min_value=1,
    value=360,
    step=1,
)

# Convert interest rates from percentages to decimals
interest_rate_range = np.arange(
    interest_rate_min / 100,
    interest_rate_max / 100 + interest_rate_step / 100,
    interest_rate_step / 100,
)

# Button to perform calculation
if st.button("Beregn kostnader"):
    if interest_rate_min >= interest_rate_max:
        st.error("Minste rentesats må være mindre enn største rentesats")
    else:
        # Call the function and generate the dataframe
        df = interest_rate_sensitivity_cached(
            houseprice_nok, interest_rate_range, ammortisation_periods
        )

        # Format the dataframe
        df["Rentesats"] = df["Rentesats"] * 100  # Convert to percentage
        df["Månedlig lånekostnad"] = df["Månedlig lånekostnad"].round(0)

        # Create a custom color scale
        custom_color_scale = px.colors.sample_colorscale(
            "OrRd", [i / 10 for i in range(3, 9)]
        )

        # Create a line chart with adjusted OrRd color gradient
        fig_line = go.Figure()
        fig_line.add_trace(
            go.Scatter(
                x=df["Rentesats"],
                y=df["Månedlig lånekostnad"],
                mode="lines+markers",
                line=dict(color=custom_color_scale[-1], width=2),
                marker=dict(
                    size=8,
                    color=df["Rentesats"],
                    colorscale=custom_color_scale,
                    colorbar=dict(title="Rentesats (%)"),
                    showscale=True,
                ),
            )
        )
        fig_line.update_layout(
            title="Månedlig lånekostnad vs. Rentesats",
            xaxis_title="Rentesats (%)",
            yaxis_title="Månedlig lånekostnad (NOK)",
            hovermode="x unified",
        )
        st.plotly_chart(fig_line)

        # Display the table in an expandable section
        with st.expander("Vis detaljert tabell"):
            # Display the table with improved formatting
            st.dataframe(
                df.style.format(
                    {
                        "Månedlig lånekostnad": "{:,.0f} kr",
                        "Rentesats": "{:.2f}%",
                    }
                )
                .set_properties(**{"text-align": "right"})
                .set_table_styles(
                    [
                        {
                            "selector": "th",
                            "props": [
                                ("text-align", "center"),
                                ("font-weight", "bold"),
                            ],
                        },
                        {"selector": "td", "props": [("padding", "8px")]},
                    ]
                ),
                use_container_width=True,
            )

# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 2024

@author: Benedikt Goodman
"""

import streamlit as st
import numpy as np
import toml
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from functions.calc_funcs import scenario_analysis_electricity_costs  # noqa: E402
from functions.plot_funcs import create_heatmap_divergent_hover  # noqa: E402
from functions.metric_cards import electricity_metric_cards  # noqa: E402
from functions import util_funcs  # noqa: E402

# Load constants from constants.toml
variables = toml.load(project_root.joinpath("variables.toml"))["electricity"]


@st.cache_data
def calculate_electricity_costs(
    kwh_usage_range, kwh_price_range, markup_nok, fixed_cost_nok
):
    return scenario_analysis_electricity_costs(
        kwh_usage_range=np.linspace(kwh_usage_range[0], kwh_usage_range[1], 50),
        kwh_price_range=np.linspace(kwh_price_range[0], kwh_price_range[1], 50),
        markup_nok=markup_nok,
        fixed_cost_nok=fixed_cost_nok,
    )


st.set_page_config(layout="centered")
st.title("Beregning av månedlige strømkostnader")

st.write("""
⚡💡 Få kontroll på strømregningen din!

🔌 Estimer månedlige kostnader
🇳🇴 Inkluderer norsk strømstøtte

Slik gjør du det:
1️⃣ Juster sliderne for forbruk og priser
2️⃣ Se hvordan valgene påvirker totalkostnaden
3️⃣ Klikk "Beregn kostnader" for resultatet

""")

kwh_usage_range = st.slider(
    variables["KWH_USAGE_RANGE_LABEL"],
    min_value=variables["KWH_USAGE_RANGE_MIN"],
    max_value=variables["KWH_USAGE_RANGE_MAX"],
    value=tuple(variables["KWH_USAGE_RANGE_DEFAULT"]),
    step=variables["KWH_USAGE_RANGE_STEP"],
)
kwh_usage_range = util_funcs.ensure_range(
    kwh_usage_range,
    variables["KWH_USAGE_RANGE_MIN"],
    variables["KWH_USAGE_RANGE_MAX"],
    variables["KWH_USAGE_RANGE_STEP"],
)

kwh_price_range = st.slider(
    variables["KWH_PRICE_RANGE_LABEL"],
    min_value=variables["KWH_PRICE_RANGE_MIN"],
    max_value=variables["KWH_PRICE_RANGE_MAX"],
    value=tuple(variables["KWH_PRICE_RANGE_DEFAULT"]),
    step=variables["KWH_PRICE_RANGE_STEP"],
)
kwh_price_range = util_funcs.ensure_range(
    kwh_price_range,
    variables["KWH_PRICE_RANGE_MIN"],
    variables["KWH_PRICE_RANGE_MAX"],
    variables["KWH_PRICE_RANGE_STEP"],
)

markup_nok = st.number_input(
    variables["MARKUP_NOK_LABEL"],
    value=variables["MARKUP_NOK_DEFAULT"],
    min_value=variables["MARKUP_NOK_MIN"],
    max_value=variables["MARKUP_NOK_MAX"],
    step=variables["MARKUP_NOK_STEP"],
)
fixed_cost_nok = st.number_input(
    variables["FIXED_COST_ELECTRICITY_LABEL"],
    value=variables["FIXED_COST_ELECTRICITY_DEFAULT"],
    min_value=variables["FIXED_COST_ELECTRICITY_MIN"],
    max_value=variables["FIXED_COST_ELECTRICITY_MAX"],
    step=variables["FIXED_COST_ELECTRICITY_STEP"],
)

# Add a button to trigger the calculation
if st.button("Beregn kostnader"):
    df = calculate_electricity_costs(
        kwh_usage_range, kwh_price_range, markup_nok, fixed_cost_nok
    )

    st.subheader("Oppsummert kostnadsbilde")
    electricity_metric_cards(df)

    st.plotly_chart(
        create_heatmap_divergent_hover(
            df,
            x_column="kWh Price (NOK)",
            y_column="kWh Usage",
            z_column="Total Cost (NOK)",
            title="Strømkostnader",
            x_axis_title="Pris per kWh (NOK)",
            y_axis_title="Strømforbruk (kWh)",
            colorbar_title="Totalkostnad (NOK)",
        ),
        use_container_width=True,
    )

st.write("""
**Om strømstøtteordningen**
- Staten dekker 90% av strømprisen som overstiger 70 øre per kWh.
- Støtten beregnes time for time og er basert på spotprisen i ditt prisområde.
- Ordningen gjelder for forbruk opp til 5000 kWh per måned.
- Støtten trekkes automatisk fra på strømregningen din.
""")

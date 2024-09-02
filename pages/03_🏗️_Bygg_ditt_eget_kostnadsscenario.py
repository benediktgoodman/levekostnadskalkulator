# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 2024

@author: Benedikt Goodman
"""

import streamlit as st
from pathlib import Path
import sys
import toml
import numpy as np


# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))


from functions.calc_funcs import (  # noqa: E402
    monthly_price_calculator_scenarios,
    calculate_amortization_schedule,
)

from functions.formatters import format_interest_rate  # noqa: E402

from functions.plot_funcs import (  # noqa: E402
    create_cost_breakdown_sunburst,
    create_interest_rate_sensitivity_chart,
    create_amortization_chart,
)

# Load constants from variables.toml
variables = toml.load(project_root.joinpath("variables.toml"))

st.set_page_config(layout="wide")
st.title(variables["general"]["APP_TITLE"])

st.write("""
🏠💡 Utforsk din fremtidige boligøkonomi her!

Lek med tallene og se hva som skjer:
- 🏷️ Boligpris
- 📊 Eierandel
- 📈 Rente
- 💸 Andre kostnader

Se hvordan valgene dine påvirker:
- 📅 Månedlige utgifter
- 🔮 Langsiktige kostnader

Perfekt for deg som:
- 🤔 Vurderer boligkjøp solo
- 👫 Planlegger kjøp med andre

👉 Juster variablene og klikk "Beregn scenario" for å se din økonomiske fremtid!
""")

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = None

# Ownership splitting
with st.container():
    st.subheader("Eierskap")
    ownership_fraq = st.slider(
        variables["ownership"]["OWNERSHIP_FRAQ_SLIDER_LABEL"],
        min_value=variables["ownership"]["OWNERSHIP_FRAQ_MIN"],
        max_value=variables["ownership"]["OWNERSHIP_FRAQ_MAX"],
        value=variables["ownership"]["OWNERSHIP_FRAQ_DEFAULT"],
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

# Housing Loan
with st.container():
    st.subheader("Boliglån")
    houseprice_range = st.slider(
        variables["house_price"]["HOUSEPRICE_SLIDER_LABEL"],
        min_value=variables["house_price"]["HOUSEPRICE_MIN"],
        max_value=variables["house_price"]["HOUSEPRICE_MAX"],
        value=tuple(variables["house_price"]["HOUSEPRICE_DEFAULT"]),
        step=variables["house_price"]["HOUSEPRICE_STEP"],
    )

    ammortisation_periods = st.number_input(
        variables["loan"]["AMMORTISATION_PERIOD_LABEL"],
        min_value=variables["loan"]["AMMORTISATION_PERIOD_MIN"],
        max_value=variables["loan"]["AMMORTISATION_PERIOD_MAX"],
        value=variables["loan"]["AMMORTISATION_PERIOD_DEFAULT"],
    )
    ek = st.number_input(
        variables["loan"]["EK_LABEL"],
        value=variables["loan"]["EK_DEFAULT"],
        step=variables["loan"]["EK_STEP"],
    )

    interest_rate_range = st.slider(
        variables["interest_rate"]["INTEREST_RATE_SLIDER_LABEL"],
        min_value=variables["interest_rate"]["INTEREST_RATE_MIN"],
        max_value=variables["interest_rate"]["INTEREST_RATE_MAX"],
        value=tuple(variables["interest_rate"]["INTEREST_RATE_DEFAULT"]),
        step=variables["interest_rate"]["INTEREST_RATE_STEP"],
    )

    transaction_costs = st.number_input(
        variables["transaction_costs"]["TRANSACTION_COSTS_LABEL"],
        value=variables["transaction_costs"]["TRANSACTION_COSTS_DEFAULT"],
        step=variables["transaction_costs"]["TRANSACTION_COSTS_STEP"],
    )

# Electricity costs
with st.container():
    st.subheader("Strøm")
    kwh_usage_range = st.slider(
        variables["electricity"]["KWH_USAGE_RANGE_LABEL"],
        min_value=variables["electricity"]["KWH_USAGE_RANGE_MIN"],
        max_value=variables["electricity"]["KWH_USAGE_RANGE_MAX"],
        value=variables["electricity"]["KWH_USAGE_RANGE_DEFAULT"][0],
        step=variables["electricity"]["KWH_USAGE_RANGE_STEP"],
        key="kwh_usage_range",
    )

    kwh_price_range = st.slider(
        variables["electricity"]["KWH_PRICE_RANGE_LABEL"],
        min_value=variables["electricity"]["KWH_PRICE_RANGE_MIN"],
        max_value=variables["electricity"]["KWH_PRICE_RANGE_MAX"],
        value=variables["electricity"]["KWH_PRICE_RANGE_DEFAULT"][0],
        step=variables["electricity"]["KWH_PRICE_RANGE_STEP"],
        key="kwh_price_range",
    )

    markup_nok = st.number_input(
        variables["electricity"]["MARKUP_NOK_LABEL"],
        value=variables["electricity"]["MARKUP_NOK_DEFAULT"],
        key="markup_nok",
    )
    fixed_cost_electricity = st.number_input(
        variables["electricity"]["FIXED_COST_ELECTRICITY_LABEL"],
        value=variables["electricity"]["FIXED_COST_ELECTRICITY_DEFAULT"],
        key="fixed_cost_nok",
    )

# Other fixed cost section
with st.container():
    st.subheader("Faste kostnader")
    fixed_cost_house = st.number_input(
        variables["fixed_costs"]["FIXED_COST_HOUSE_LABEL"],
        value=variables["fixed_costs"]["FIXED_COST_HOUSE_DEFAULT"],
        step=variables["fixed_costs"]["FIXED_COST_HOUSE_STEP"],
    )

    person_a_fixed_costs = st.number_input(
        variables["fixed_costs"]["PERSON_A_FIXED_COSTS_LABEL"],
        value=variables["fixed_costs"]["PERSON_A_FIXED_COSTS_DEFAULT"],
        step=variables["fixed_costs"]["PERSON_A_FIXED_COSTS_STEP"],
    )
    person_b_fixed_costs = st.number_input(
        variables["fixed_costs"]["PERSON_B_FIXED_COSTS_LABEL"],
        value=variables["fixed_costs"]["PERSON_B_FIXED_COSTS_DEFAULT"],
        step=variables["fixed_costs"]["PERSON_B_FIXED_COSTS_STEP"],
    )

# Convert interest rates from percentages to decimals
interest_rates_decimal = np.arange(
    interest_rate_range[0] / 100, interest_rate_range[1] / 100 + 0.005, 0.0025
)


# Calculate scenarios
@st.cache_data
def calculate_scenarios(
    houseprice_range,
    interest_rates_decimal,
    fixed_cost_house,
    kwh_usage_range,
    kwh_price_range,
    markup_nok,
    fixed_cost_electricity,
    ammortisation_periods,
    person_a_fixed_costs,
    person_b_fixed_costs,
    transaction_costs,
    ek,
    ownership_fraq,
):
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
        ownership_fraq_range=[ownership_fraq / 100],  # Convert percentage to fraction
    )
    df["interest_rate"] = df["interest_rate"].round(5)
    return df


# Button to perform calculation
if st.button("Beregn scenario"):
    # Calculate and store results
    st.session_state.df = calculate_scenarios(
        houseprice_range,
        interest_rates_decimal,
        fixed_cost_house,
        kwh_usage_range,
        kwh_price_range,
        markup_nok,
        fixed_cost_electricity,
        ammortisation_periods,
        person_a_fixed_costs,
        person_b_fixed_costs,
        transaction_costs,
        ek,
        ownership_fraq,
    )

    # Display results
    if st.session_state.df is not None:
        st.subheader("Resultater")

        # Filters for sunburst charts
        col1, col2 = st.columns(2)
        with col1:
            selected_house_price = st.selectbox(
                "Velg boligpris", st.session_state.df["house_price"].unique()
            )
        with col2:
            formatted_rates = [
                format_interest_rate(rate)
                for rate in st.session_state.df["interest_rate"].unique()
            ]
            selected_interest_rate_str = st.selectbox("Velg rentesats", formatted_rates)
            selected_interest_rate = round(
                float(selected_interest_rate_str.strip("%")) / 100, 5
            )

        filtered_df = st.session_state.df[
            (st.session_state.df["house_price"] == selected_house_price)
            & (st.session_state.df["interest_rate"] == selected_interest_rate)
        ]

        # Summary Dashboard
        st.subheader("Sammendrag")
        col1, col2, col3, col4 = st.columns(4)

        total_loan = selected_house_price - ek
        monthly_payment = filtered_df["monthly_loan_payment"].iloc[0]
        total_interest = monthly_payment * ammortisation_periods - total_loan
        loan_to_value = (total_loan / selected_house_price) * 100

        col1.metric(
            "Totalt lån",
            f"{total_loan:,.0f} kr",
            help="Det totale lånebeløpet etter fratrekk av egenkapital",
        )
        col2.metric(
            "Månedlig betaling",
            f"{monthly_payment:,.0f} kr",
            help="Den totale månedlige betalingen inkludert renter og avdrag",
        )
        col3.metric(
            "Total rentebelastning",
            f"{total_interest:,.0f} kr",
            help="Totalt rentebeløp som betales over hele lånets løpetid",
        )
        col4.metric(
            "Belåningsgrad",
            f"{loan_to_value:.1f}%",
            help="Forholdet mellom lånebeløp og boligens verdi, uttrykt som en prosentandel",
        )

        # Cost Breakdown
        st.subheader("Kostnadsanalyse")
        st.write("""
        Disse diagrammene viser hvordan de totale månedlige kostnadene er fordelt mellom 
        ulike kategorier for hver person. Dette inkluderer boliglån, faste boligkostnader, 
        strømutgifter og andre personlige utgifter.
        """)

        # Create two columns for side-by-side sunburst charts and metric boxes
        col1, col2 = st.columns(2)

        with col1:
            # Metric box for Person A
            total_cost_a = filtered_df["a_total"].iloc[0]
            st.metric(
                label="Person A: Total månedlig kostnad",
                value=f"{total_cost_a:.2f} kr",
                help="Den totale månedlige kostnaden for Person A, inkludert lån, strøm, og andre faste kostnader",
            )

            fig_a = create_cost_breakdown_sunburst(filtered_df, "A")
            st.plotly_chart(fig_a, use_container_width=True)

        with col2:
            # Metric box for Person B
            total_cost_b = filtered_df["b_total"].iloc[0]
            st.metric(
                label="Person B: Total månedlig kostnad",
                value=f"{total_cost_b:.2f} kr",
                help="Den totale månedlige kostnaden for Person B, inkludert lån, strøm, og andre faste kostnader",
            )

            fig_b = create_cost_breakdown_sunburst(filtered_df, "B")
            st.plotly_chart(fig_b, use_container_width=True)

        loan_amount = selected_house_price - ek
        ownership_fraq = filtered_df["ownership_fraq"].iloc[0]

        # Interest Rate Sensitivity
        st.subheader("Rentesensitivitetsanalyse")
        st.write("""
        Disse grafene viser hvordan den månedlige lånebetalingen endrer seg med 
        ulike rentesatser for hver person. Kort sagt viser de hvordan 
        renteendringer påvirker dine månedlige utgifter.
        """)

        col1, col2 = st.columns(2)
        with col1:
            fig_sensitivity_a = create_interest_rate_sensitivity_chart(
                loan_amount * ownership_fraq, ammortisation_periods, interest_rate_range
            )
            fig_sensitivity_a.update_layout(
                title="Person A: Månedlig lånekostnad vs. Rentesats"
            )
            st.plotly_chart(fig_sensitivity_a, use_container_width=True)

        with col2:
            fig_sensitivity_b = create_interest_rate_sensitivity_chart(
                loan_amount * (1 - ownership_fraq),
                ammortisation_periods,
                interest_rate_range,
            )
            fig_sensitivity_b.update_layout(
                title="Person B: Månedlig lånekostnad vs. Rentesats"
            )
            st.plotly_chart(fig_sensitivity_b, use_container_width=True)

        loan_amount_a = loan_amount * ownership_fraq
        loan_amount_b = loan_amount * (1 - ownership_fraq)

        schedule_a = calculate_amortization_schedule(
            loan_amount_a, selected_interest_rate, ammortisation_periods
        )
        schedule_b = calculate_amortization_schedule(
            loan_amount_b, selected_interest_rate, ammortisation_periods
        )

        # Amortization Schedule
        st.subheader("Nedbetalingsplan")
        st.write("""
        Disse grafene viser hvordan lånebalansen, kumulative avdrag og kumulative 
        renter endrer seg over tid for hver person. Dette gir deg en oversikt over 
        hvordan lånet vil bli nedbetalt gjennom hele låneperioden.
        """)

        col1, col2 = st.columns(2)

        with col1:
            fig_a = create_amortization_chart(schedule_a, "Person A")
            st.plotly_chart(fig_a, use_container_width=True)

        with col2:
            fig_b = create_amortization_chart(schedule_b, "Person B")
            st.plotly_chart(fig_b, use_container_width=True)

        # Data display and download options
        st.subheader("Data og eksport")
        data_option = st.selectbox("Velg datavisning", ["Vis data", "Last ned data"])

        if data_option == "Vis data":
            st.dataframe(st.session_state.df)
        elif data_option == "Last ned data":
            csv = st.session_state.df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Last ned CSV",
                data=csv,
                file_name="kostnadsscenario_data.csv",
                mime="text/csv",
            )

import streamlit as st
import os
from pathlib import Path
import toml
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# Import new functions
from functions.calc_functions import (
    monthly_price_calculator_scenarios,
    #calculate_total_monthly_costs,
)

from functions.plot_figures import(
    calculate_cost_breakdown,
    calculate_loan_details,
    create_monthly_costs_chart,
    create_cost_breakdown_chart,
    create_ownership_chart,
    create_loan_details_chart,
    create_long_term_projection,
    calculate_sensitivity,
    create_scenario_comparison
)

# Load constants from constants.toml
variables = toml.load("variables.toml")['constants']

@st.cache_data
def load_data(inputs):
    """Load and cache data based on inputs."""
    return monthly_price_calculator_scenarios(**inputs)

def create_download_link(val, filename):
    """Create a download link for the PDF."""
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Last ned PDF rapport</a>'

def main():
    st.set_page_config(layout='wide')
    st.title(variables["APP_TITLE"])
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Juster parametere")
        houseprice = st.slider(variables["HOUSEPRICE_SLIDER_LABEL"],
                               min_value=variables["HOUSEPRICE_MIN"], 
                               max_value=variables["HOUSEPRICE_MAX"], 
                               value=variables["HOUSEPRICE_DEFAULT"][0], 
                               step=variables["HOUSEPRICE_STEP"])
        
        interest_rate = st.slider(variables["INTEREST_RATE_SLIDER_LABEL"],
                                  min_value=variables["INTEREST_RATE_MIN"], 
                                  max_value=variables["INTEREST_RATE_MAX"], 
                                  value=variables["INTEREST_RATE_DEFAULT"][0], 
                                  step=variables["INTEREST_RATE_STEP"]) / 100
        
        ammortisation_periods = st.number_input(variables["AMMORTISATION_PERIOD_LABEL"], 
                                                min_value=variables["AMMORTISATION_PERIOD_MIN"], 
                                                max_value=variables["AMMORTISATION_PERIOD_MAX"], 
                                                value=variables["AMMORTISATION_PERIOD_DEFAULT"])
        
        ek = st.number_input(variables["EK_LABEL"], 
                             value=variables["EK_DEFAULT"], 
                             step=variables["EK_STEP"])
        
        ownership_fraq = st.slider(variables["OWNERSHIP_FRAQ_SLIDER_LABEL"],
                                   min_value=variables["OWNERSHIP_FRAQ_MIN"], 
                                   max_value=variables["OWNERSHIP_FRAQ_MAX"], 
                                   value=variables["OWNERSHIP_FRAQ_DEFAULT"])
        
        elprice = st.number_input(variables["ELPRICE_SLIDER_LABEL"],
                                  min_value=variables["ELPRICE_MIN"], 
                                  max_value=variables["ELPRICE_MAX"], 
                                  value=variables["ELPRICE_DEFAULT"])
        
        fixed_cost_house = st.number_input(variables["FIXED_COST_HOUSE_LABEL"], 
                                           value=variables["FIXED_COST_HOUSE_DEFAULT"], 
                                           step=variables["FIXED_COST_HOUSE_STEP"])
        
        person_a_fixed_costs = st.number_input(variables["PERSON_A_FIXED_COSTS_LABEL"], 
                                               value=variables["PERSON_A_FIXED_COSTS_DEFAULT"], 
                                               step=variables["PERSON_A_FIXED_COSTS_STEP"])
        
        person_b_fixed_costs = st.number_input(variables["PERSON_B_FIXED_COSTS_LABEL"], 
                                               value=variables["PERSON_B_FIXED_COSTS_DEFAULT"], 
                                               step=variables["PERSON_B_FIXED_COSTS_STEP"])

    # Calculate results
    inputs = {
        'houseprice_range': [houseprice],
        'interest_rate_range': [interest_rate],
        'fixed_cost_house_range': [fixed_cost_house],
        'kwh_usage_range': [5000],  # Add a default value or create a slider for this
        'kwh_price_range': [elprice],
        'markup_nok_range': [0.1],  # Add a default value or create a slider for this
        'fixed_cost_electricity_range': [100],  # Add a default value or create a slider for this
        'ammortisation_periods_range': [ammortisation_periods],
        'person_a_fixed_costs_range': [person_a_fixed_costs],
        'person_b_fixed_costs_range': [person_b_fixed_costs],
        'transaction_costs_range': [0],  # Add a default value or create an input for this
        'ek_range': [ek],
        'ownership_fraq_range': [ownership_fraq/100]
    }

    @st.cache_data
    def load_data(inputs):
        """Load and cache data based on inputs."""
        return monthly_price_calculator_scenarios(**inputs)

    results = load_data(inputs)
    
    # Extract relevant data from results
    monthly_payment = results['monthly_loan_payment'].iloc[0]
    person_a_total = results['a_total'].iloc[0]
    person_b_total = results['b_total'].iloc[0]
    
    # Create dashboard
    st.header("Boligkostnader Sammendrag")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Månedlige Kostnader Oversikt")
        monthly_costs_chart = create_monthly_costs_chart(person_a_total, person_b_total)
        st.plotly_chart(monthly_costs_chart, use_container_width=True)
        
        st.subheader("Kostnadsfordeling")
        cost_breakdown = calculate_cost_breakdown(monthly_payment, elprice, fixed_cost_house)
        cost_breakdown_chart = create_cost_breakdown_chart(cost_breakdown)
        st.plotly_chart(cost_breakdown_chart, use_container_width=True)
    
    with col2:
        st.subheader("Lånedetaljer")
        loan_amount = houseprice - ek
        monthly_payment, first_month_interest, first_month_principal = calculate_loan_details(loan_amount, interest_rate, ammortisation_periods)
        st.write(f"Lånebeløp: {loan_amount:,.0f} NOK")
        st.write(f"Rente: {interest_rate:.2%}")
        st.write(f"Nedbetalingstid: {ammortisation_periods} måneder")
        loan_details_chart = create_loan_details_chart(first_month_interest, first_month_principal)
        st.plotly_chart(loan_details_chart, use_container_width=True)
        
        st.subheader("Eierskapsfordeling")
        ownership_chart = create_ownership_chart(ownership_fraq, 100-ownership_fraq)
        st.plotly_chart(ownership_chart, use_container_width=True)
    
    st.subheader("Langsiktig Kostnadsprognose")
    long_term_projection = create_long_term_projection(monthly_payment, ammortisation_periods)
    st.plotly_chart(long_term_projection, use_container_width=True)
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        total_interest = monthly_payment * ammortisation_periods - loan_amount
        st.metric("Total Rentebetaling", f"{total_interest:,.0f} NOK")
    
    with col4:
        payoff_date = pd.Timestamp.now() + pd.DateOffset(months=ammortisation_periods)
        st.metric("Nedbetalt Dato", payoff_date.strftime('%d.%m.%Y'))
    
    with col5:
        sensitivity = calculate_sensitivity(monthly_payment, interest_rate)
        st.metric("Sensitivitet (1% renteøkning)", f"{sensitivity:.2%}")
    
    # Scenario comparison
    if 'scenarios' not in st.session_state:
        st.session_state.scenarios = []
    
    if st.button('Lagre scenario'):
        current_scenario = {
            'Boligpris': houseprice,
            'Rente': interest_rate,
            'Månedlig kostnad A': person_a_total,
            'Månedlig kostnad B': person_b_total
        }
        st.session_state.scenarios.append(current_scenario)
    
    if st.session_state.scenarios:
        st.subheader("Scenario Sammenligning")
        current_scenario = {
            'Boligpris': houseprice,
            'Rente': interest_rate,
            'Månedlig kostnad A': person_a_total,
            'Månedlig kostnad B': person_b_total
        }
        comparison_df = create_scenario_comparison(current_scenario, st.session_state.scenarios)
        st.dataframe(comparison_df)
    
    # Generate PDF report
    if st.button('Generer PDF rapport'):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Boligkostnader Rapport", ln=1, align="C")
        pdf.cell(200, 10, txt=f"Boligpris: {houseprice:,.0f} NOK", ln=1)
        pdf.cell(200, 10, txt=f"Rente: {interest_rate:.2%}", ln=1)
        pdf.cell(200, 10, txt=f"Månedlig kostnad Person A: {person_a_total:,.0f} NOK", ln=1)
        pdf.cell(200, 10, txt=f"Månedlig kostnad Person B: {person_b_total:,.0f} NOK", ln=1)
        
        html = create_download_link(pdf.output(dest="S").encode("latin-1"), "boligkostnader_rapport")
        st.markdown(html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
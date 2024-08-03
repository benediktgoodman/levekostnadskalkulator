import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from pydantic import validate_call

import os
from pathlib import Path

# Finn rotmappe i prosjekt
script_path = Path(os.getcwd())

while "app.py" not in os.listdir():
    os.chdir("../")

from functions.calc_functions import (
    loan_calc,
    interest_rate_sensitivity
)

os.chdir(script_path)

def main():

    # Streamlit app layout
    st.title('Hva vil lånet ditt egentlig koste deg i måneden?')
    # st.write(
    #     """Hva vil lånet ditt koste i måneden med en annen rente enn den du har i dag?
    #     Det er ikke så lett å holde styr på med alle renteendringene som skjer både støtt og stadig.
        
    #     """
    # )

    # Cache functions that should be used
    loan_calc_cached = st.cache_data(loan_calc)
    interest_rate_sensitivity_cached = st.cache_data(interest_rate_sensitivity)

    # User inputs
    houseprice_nok = st.number_input('Hvor mye låner du?:', min_value=100000, value=2500000, step=100000)
    interest_rate_min = st.number_input('Hva er minste rentesats? (%):', min_value=0.0, value=1.0, step=0.1, format='%.2f')
    interest_rate_max = st.number_input('Hva er største rentsats (%):', min_value=0.0, value=5.0, step=0.1, format='%.2f')
    interest_rate_step = st.number_input('Intervallbredde på renteendringer (%):', min_value=0.25, value=0.25, step=0.25, format='%.2f')
    ammortisation_periods = st.number_input('Hva er tilbakebetalingstiden på lånet? (i antall måneder):', min_value=1, value=360, step=1)
        

    # Convert interest rates from percentages to decimals
    interest_rate_range = np.arange(interest_rate_min / 100, interest_rate_max / 100 + interest_rate_step / 100, interest_rate_step / 100)

# Button to perform calculation
    if st.button('Beregn kostnader'):
        if interest_rate_min >= interest_rate_max:
            st.error('Minste rentesats må være større enn største rentesats')
        else:
            # Call the function and generate the dataframe
            df = interest_rate_sensitivity_cached(houseprice_nok, interest_rate_range, ammortisation_periods)
            styled_df = df.style.format({
                'Månedlig lånekostnad' : "kr {:.0f}",
                'Rentesats': "{:.2%}",
            })
            
            st.subheader('Låneutgifter basert på oppgit renteintervall')
            st.table(styled_df)
            
            # # Plotting using Plotly Express
            # fig = px.bar(
            #     df,
            #     x='Rentesats',
            #     y='Månedlig lånekostnad',
            #     labels={'Rentesats': 'Rentesats (%)', 'Månedlig lånekostnad': 'Månedlig lånekostnad (NOK)'},
            #     title='Hvor mye lånet ditt vil koste dersom renten endrer seg',
            # )
            
            # # Show figure
            # st.plotly_chart(fig, use_container_width=True)
            
if __name__ == '__main__':
    main()
    

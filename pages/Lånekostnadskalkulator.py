import streamlit as st
import numpy as np
import pandas as pd  # noqa: F401
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path

# Finn rotmappe i prosjekt
script_path = Path(os.getcwd())
while "app.py" not in os.listdir():
    os.chdir("../")
from functions.calc_functions import (  # noqa: E402
    loan_calc,
    interest_rate_sensitivity
)
os.chdir(script_path)

def main():
    # Streamlit app layout
    st.title('Hva vil lånet ditt egentlig koste deg i måneden?')
    st.write("""
    Denne kalkulatoren hjelper deg å forstå hvordan endringer i renten kan påvirke hvor mye du betaler per måned for et boliglån. 
    Ved å oppgi et intervall av rentesatser, fra lav til høy, kan du se hvordan kostnadene varierer under ulike 
    økonomiske forhold. Renter kan svinge over tid, og har stor effekt på hvor mye man betaler som låntaker. 
    """, )
    
    # Cache functions that should be used
    loan_calc_cached = st.cache_data(loan_calc)  # noqa: F841
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
            st.error('Minste rentesats må være mindre enn største rentesats')
        else:
            # Call the function and generate the dataframe
            df = interest_rate_sensitivity_cached(houseprice_nok, interest_rate_range, ammortisation_periods)
            
            # Format the dataframe
            df['Rentesats'] = df['Rentesats'] * 100  # Convert to percentage
            df['Månedlig lånekostnad'] = df['Månedlig lånekostnad'].round(0)
            
            # Create a custom color scale
            custom_color_scale = px.colors.sample_colorscale("OrRd", [i/10 for i in range(3, 9)])
            
            # Create a line chart with adjusted OrRd color gradient
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=df['Rentesats'],
                y=df['Månedlig lånekostnad'],
                mode='lines+markers',
                line=dict(color=custom_color_scale[-1], width=2),
                marker=dict(
                    size=8,
                    color=df['Rentesats'],
                    colorscale=custom_color_scale,
                    colorbar=dict(title='Rentesats (%)'),
                    showscale=True
                )
            ))
            fig_line.update_layout(
                title='Månedlig lånekostnad vs. Rentesats',
                xaxis_title='Rentesats (%)',
                yaxis_title='Månedlig lånekostnad (NOK)',
                hovermode='x unified'
            )
            st.plotly_chart(fig_line)
            
            # # Create a bar chart with adjusted OrRd color scheme
            # fig_bar = px.bar(df, x='Rentesats', y='Månedlig lånekostnad', 
            #                  title='Månedlig lånekostnad for ulike rentesatser',
            #                  labels={'Rentesats': 'Rentesats (%)', 
            #                          'Månedlig lånekostnad': 'Månedlig lånekostnad (NOK)'},
            #                  color='Rentesats',
            #                  color_continuous_scale=custom_color_scale)
            # fig_bar.update_layout(yaxis_title='Månedlig lånekostnad (NOK)')
            # st.plotly_chart(fig_bar)
            
            # Display the table in an expandable section
            with st.expander("Vis detaljert tabell"):
                # Display the table with improved formatting
                st.dataframe(
                    df.style
                    .format({
                        'Månedlig lånekostnad': "{:,.0f} kr",
                        'Rentesats': "{:.2f}%",
                    })
                    .set_properties(**{'text-align': 'right'})
                    .set_table_styles([
                        {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold')]},
                        {'selector': 'td', 'props': [('padding', '8px')]},
                    ]),
                    use_container_width=True
                )

if __name__ == '__main__':
    main()
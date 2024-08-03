import streamlit as st

def electricity_metric_cards(df):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Laveste kostnad",
            value=f"kr{df['Total Cost (NOK)'].min():.2f}",
        )

    with col2:
        st.metric(
            label="Gjennomsnittlig kostnad",
            value=f"kr{df['Total Cost (NOK)'].mean():.2f}",
        )
        
    with col3:
        st.metric(
            label="Høyeste kostnad",
            value=f"kr{df['Total Cost (NOK)'].max():.2f}",

        )
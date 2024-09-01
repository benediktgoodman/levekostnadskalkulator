import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import os
from pathlib import Path

# Find root folder in project
script_path = Path(os.getcwd())

while "Boligkostnadskalkulatoren.py" not in os.listdir():
    os.chdir("../")

from functions.calc_functions import loan_calc

# Change working dir back to script
os.chdir(script_path)

# Set the default theme for all charts
template = 'seaborn'

def create_interest_rate_sensitivity_chart(loan_amount, periods, interest_rate_range):
    interest_rates = np.arange(interest_rate_range[0], interest_rate_range[1] + 0.1, 0.25)
    monthly_payments = [loan_calc(loan_amount, rate/100, periods) for rate in interest_rates]
   
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=interest_rates,
        y=monthly_payments,
        mode='lines+markers',
    ))
    fig.update_layout(
        title='Rentesensitivitetsanalyse',
        xaxis_title='Rentesats (%)',
        yaxis_title='Månedlig betaling (NOK)',
        hovermode='x unified',
        height=500,
        template=template,
    )
    return fig

def create_cost_breakdown_sunburst(df, person):
    if person == 'A':
        loan_payment = df['monthly_loan_payment'] * df['ownership_fraq']
        fixed_costs = df['person_a_fixed_costs']
    else:
        loan_payment = df['monthly_loan_payment'] * (1 - df['ownership_fraq'])
        fixed_costs = df['person_b_fixed_costs']
   
    sunburst_data = pd.DataFrame({
        'kategori': ['Boligkostnader', 'Boligkostnader', 'Boligkostnader', 'Personlige kostnader'],
        'underkategori': ['Lånebetaling', 'Faste boligkostnader', 'Strøm', 'Andre faste kostnader'],
        'verdi': [
            loan_payment.iloc[0],
            df['fixed_cost_house'].iloc[0] / 2,  # Assuming equal split
            df['el_cost'].iloc[0] / 2,  # Assuming equal split
            fixed_costs.iloc[0]
        ]
    })
   
    # Sort the dataframe so that 'Boligkostnader' come first
    sunburst_data['sort_order'] = sunburst_data['kategori'].map({'Boligkostnader': 0, 'Personlige kostnader': 1})
    sunburst_data = sunburst_data.sort_values('sort_order')
   
    fig = px.sunburst(
        sunburst_data,
        path=['kategori', 'underkategori'],
        values='verdi',
        color='underkategori',
        title="Kostnadsfordeling",
        template=template
    )
    fig.update_traces(textinfo='label+value+percent parent')
    fig.update_layout(
        height=600,
        width=600,
        margin=dict(t=30, l=0, r=0, b=0)
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Beløp: kr %{value:.2f}<br>Andel: %{percentParent:.1%}<extra></extra>'
    )
    
    return fig

def create_amortization_chart(schedule, title):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=schedule['Month'], y=schedule['Remaining Balance'], name="Gjenstående saldo")
    )
    fig.add_trace(
        go.Scatter(x=schedule['Month'], y=schedule['Principal'].cumsum(), name="Kumulativt avdrag")
    )
    fig.add_trace(
        go.Scatter(x=schedule['Month'], y=schedule['Interest'].cumsum(), name="Kumulative renter")
    )

    fig.update_layout(
        title=title,
        xaxis_title="Måned",
        yaxis_title="Beløp (NOK)",
        legend=dict(x=0, y=1, traceorder="normal"),
        template=template
    )

    return fig

def create_heatmap_divergent_hover(df, x_column, y_column, z_column, 
                                   title='Heatmap', 
                                   x_axis_title='X Axis', 
                                   y_axis_title='Y Axis', 
                                   colorbar_title='Value'):
    # Pivot the dataframe
    pivot_df = df.pivot(index=y_column, columns=x_column, values=z_column)
    
    # Calculate the median for the divergent color scale
    median_value = np.median(pivot_df.values)
    
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale='turbo',
        colorbar=dict(title=colorbar_title),
        zmid=median_value,
        zmin=df[z_column].min(),
        zmax=df[z_column].max(),
        hovertemplate=(
            f"<b>{x_axis_title}</b>: %{{x:.2f}}<br>"
            f"<b>{y_axis_title}</b>: %{{y}}<br>"
            f"<b>{colorbar_title}</b>: %{{z:.2f}}<br>"
            "<extra></extra>"
        ),
        zsmooth='fast'
    ))

    # Update the layout
    fig.update_layout(
        title=title,
        xaxis_title=x_axis_title,
        yaxis_title=y_axis_title,
        width=800,
        height=600,
        margin=dict(l=65, r=50, b=65, t=90)
    )

    return fig
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 2024

@author: Benedikt Goodman
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from functions.calc_funcs import loan_calc  # noqa: E402


# Set the default theme for all charts
template = 'seaborn'

def create_interest_rate_sensitivity_chart(loan_amount: float, periods: int, interest_rate_range: tuple[float, float]) -> go.Figure:
   """
   Create a line chart that shows the monthly payment for a loan based on a range of interest rates.

   Parameters
   ----------
   loan_amount : float
       The total amount of the loan.
   periods : int
       The number of months the loan will be amortized over.
   interest_rate_range : tuple[float, float]
       The range of interest rates to include in the chart.

   Returns
   -------
   go.Figure
       A Plotly figure object representing the interest rate sensitivity chart.
   """
   interest_rates = np.arange(interest_rate_range[0], interest_rate_range[1] + 0.1, 0.25)
   monthly_payments = loan_calc(loan_amount, interest_rates/100, periods)
  
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

def create_cost_breakdown_sunburst(df: pd.DataFrame, person: str) -> go.Figure:
   """
   Create a Plotly Sunburst chart that shows the breakdown of monthly costs for a given person.

   Parameters
   ----------
   df : pd.DataFrame
       The DataFrame containing the relevant data for the cost breakdown.
   person : str
       The person for whom the cost breakdown should be calculated ('A' or 'B').

   Returns
   -------
   go.Figure
       A Plotly figure object representing the cost breakdown sunburst chart.
   """
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

def create_amortization_chart(schedule: pd.DataFrame, title: str) -> go.Figure:
   """
   Create a Plotly line chart that shows the amortization schedule for a loan.

   Parameters
   ----------
   schedule : pd.DataFrame
       The DataFrame containing the amortization schedule data.
   title : str
       The title to be displayed on the chart.

   Returns
   -------
   go.Figure
       A Plotly figure object representing the amortization chart.
   """
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

def create_heatmap_divergent_hover(df: pd.DataFrame, x_column: str, y_column: str, z_column: str, 
                                  title: str = 'Heatmap', 
                                  x_axis_title: str = 'X Axis', 
                                  y_axis_title: str = 'Y Axis', 
                                  colorbar_title: str = 'Value') -> go.Figure:
   """
   Create a Plotly Heatmap chart with a divergent color scale and hover information.

   Parameters
   ----------
   df : pd.DataFrame
       The DataFrame containing the data to be plotted.
   x_column : str
       The name of the column to be used for the x-axis.
   y_column : str
       The name of the column to be used for the y-axis.
   z_column : str
       The name of the column to be used for the z-axis (color scale).
   title : str, optional
       The title to be displayed on the chart, by default 'Heatmap'.
   x_axis_title : str, optional
       The title to be displayed on the x-axis, by default 'X Axis'.
   y_axis_title : str, optional
       The title to be displayed on the y-axis, by default 'Y Axis'.
   colorbar_title : str, optional
       The title to be displayed on the color bar, by default 'Value'.

   Returns
   -------
   go.Figure
       A Plotly figure object representing the heatmap chart.
   """
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


def create_amortization_chart_optimized(schedule: pd.DataFrame, title: str) -> go.Figure:
    """
    Create an optimized amortization chart using Plotly.

    Args:
    schedule (Dict[str, Any]): A dictionary containing the amortization schedule data.
    title (str): The title of the chart.

    Returns:
    go.Figure: A Plotly figure object representing the amortization chart.
    """
    # Convert schedule data to numpy arrays for faster operations
    months = np.array(schedule['Month'])
    remaining_balance = np.array(schedule['Remaining Balance'])
    principal = np.array(schedule['Principal'])
    interest = np.array(schedule['Interest'])

    # Pre-compute cumulative sums
    cumulative_principal = np.cumsum(principal)
    cumulative_interest = np.cumsum(interest)

    # Create figure with all traces at once
    fig = go.Figure()
    fig.add_traces([
        go.Scatter(x=months, y=remaining_balance, name="Gjenstående saldo"),
        go.Scatter(x=months, y=cumulative_principal, name="Kumulativt avdrag"),
        go.Scatter(x=months, y=cumulative_interest, name="Kumulative renter")
    ])

    # Set layout parameters all at once
    fig.update_layout(
        title=title,
        xaxis_title="Måned",
        yaxis_title="Beløp (NOK)",
        legend=dict(x=0, y=1, traceorder="normal"),
        template=template,  # Assuming you're using a template
        hovermode="x unified"
    )

    return fig
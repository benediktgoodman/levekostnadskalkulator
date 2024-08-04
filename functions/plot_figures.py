import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd  # noqa: F401
import numpy as np

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
        zmid=median_value,  # Set the middle color to correspond to the median value
        zmin=df.values.min(),
        zmax=df.values.max(),
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




def calculate_total_monthly_costs(loan_payment, electricity_cost, fixed_costs):
    """Calculate total monthly costs."""
    return loan_payment + electricity_cost + fixed_costs

def calculate_cost_breakdown(loan_payment, electricity_cost, fixed_costs):
    """Calculate cost breakdown for treemap."""
    return pd.DataFrame({
        'Category': ['Loan Payment', 'Electricity', 'Fixed Costs'],
        'Amount': [loan_payment, electricity_cost, fixed_costs]
    })

def calculate_loan_details(loan_amount, interest_rate, loan_term):
    """Calculate loan details including monthly payment and interest vs principal."""
    monthly_rate = interest_rate / 12
    monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate) ** loan_term) / ((1 + monthly_rate) ** loan_term - 1)
    first_month_interest = loan_amount * monthly_rate
    first_month_principal = monthly_payment - first_month_interest
    return monthly_payment, first_month_interest, first_month_principal

def create_monthly_costs_chart(person_a_costs, person_b_costs):
    """Create a horizontal stacked bar chart for monthly costs."""
    fig = go.Figure(go.Bar(
        y=['Total Monthly Costs'],
        x=[person_a_costs],
        name='Person A',
        orientation='h'
    ))
    fig.add_trace(go.Bar(
        y=['Total Monthly Costs'],
        x=[person_b_costs],
        name='Person B',
        orientation='h'
    ))
    fig.update_layout(barmode='stack', height=200, margin=dict(l=0, r=0, t=0, b=0))
    return fig

def create_cost_breakdown_chart(cost_breakdown_df):
    """Create a treemap for cost breakdown."""
    fig = px.treemap(cost_breakdown_df, path=['Category'], values='Amount', height=300)
    fig.update_traces(textinfo="label+value")
    return fig

def create_ownership_chart(person_a_ownership, person_b_ownership):
    """Create a pie chart for ownership split."""
    fig = go.Figure(data=[go.Pie(labels=['Person A', 'Person B'], 
                                 values=[person_a_ownership, person_b_ownership])])
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
    return fig

def create_loan_details_chart(interest, principal):
    """Create a pie chart for interest vs principal."""
    fig = go.Figure(data=[go.Pie(labels=['Interest', 'Principal'], 
                                 values=[interest, principal])])
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0))
    return fig

def create_long_term_projection(monthly_payment, loan_term):
    """Create a line chart for long-term cost projection."""
    years = list(range(1, 11))
    total_costs = [monthly_payment * 12 * year for year in years]
    fig = go.Figure(data=go.Scatter(x=years, y=total_costs, mode='lines+markers'))
    fig.update_layout(
        xaxis_title="Years",
        yaxis_title="Total Costs (NOK)",
        height=300,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig

def calculate_sensitivity(base_monthly_payment, interest_rate):
    """Calculate sensitivity to 1% interest rate increase."""
    new_rate = interest_rate + 0.01
    # Recalculate monthly payment with new rate
    # This is a simplified calculation and might need adjustment
    new_monthly_payment = base_monthly_payment * (1 + new_rate) / (1 + interest_rate)
    sensitivity = (new_monthly_payment - base_monthly_payment) / base_monthly_payment
    return sensitivity

def create_scenario_comparison(current_scenario, saved_scenarios):
    """Create a comparison table for scenarios."""
    all_scenarios = [current_scenario] + saved_scenarios
    df = pd.DataFrame(all_scenarios)
    df['Scenario'] = ['Current'] + [f'Scenario {i+1}' for i in range(len(saved_scenarios))]
    return df.set_index('Scenario')
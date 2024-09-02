import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from functions.plot_funcs import (  # noqa: E402
    create_interest_rate_sensitivity_chart,
    create_cost_breakdown_sunburst,
    create_amortization_chart,
    create_heatmap_divergent_hover
)

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'monthly_loan_payment': [1000],
        'ownership_fraq': [0.6],
        'person_a_fixed_costs': [500],
        'person_b_fixed_costs': [600],
        'fixed_cost_house': [400],
        'el_cost': [200]
    })

@pytest.fixture
def sample_schedule():
    return pd.DataFrame({
        'Month': range(1, 13),
        'Remaining Balance': [10000 - i*100 for i in range(12)],
        'Principal': [100] * 12,
        'Interest': [50] * 12
    })

def test_create_interest_rate_sensitivity_chart():
    fig = create_interest_rate_sensitivity_chart(100000, 360, (1.0, 5.0))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == 'scatter'
    assert fig.layout.title.text == 'Rentesensitivitetsanalyse'
    assert fig.layout.xaxis.title.text == 'Rentesats (%)'
    assert fig.layout.yaxis.title.text == 'Månedlig betaling (NOK)'

def test_create_cost_breakdown_sunburst(sample_df):
    fig = create_cost_breakdown_sunburst(sample_df, 'A')
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == 'sunburst'
    assert fig.layout.title.text == 'Kostnadsfordeling'

def test_create_amortization_chart(sample_schedule):
    fig = create_amortization_chart(sample_schedule, 'Test Amortization')
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 3
    assert all(trace.type == 'scatter' for trace in fig.data)
    assert fig.layout.title.text == 'Test Amortization'
    assert fig.layout.xaxis.title.text == 'Måned'
    assert fig.layout.yaxis.title.text == 'Beløp (NOK)'

def test_create_heatmap_divergent_hover():
    df = pd.DataFrame({
        'x': [1, 2, 3] * 3,
        'y': [1, 1, 1, 2, 2, 2, 3, 3, 3],
        'z': np.random.rand(9)
    })
    fig = create_heatmap_divergent_hover(df, 'x', 'y', 'z')
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == 'heatmap'
    assert fig.layout.title.text == 'Heatmap'
    assert fig.layout.xaxis.title.text == 'X Axis'
    assert fig.layout.yaxis.title.text == 'Y Axis'

if __name__ == '__main__':
    pytest.main()
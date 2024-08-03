import plotly.graph_objects as go
import pandas as pd
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
        colorscale='RdBu_r',  # Red-White-Blue diverging colorscale
        colorbar=dict(title=colorbar_title),
        zmid=median_value,  # Set the middle color to correspond to the median value
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

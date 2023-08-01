import plotly.graph_objects as go
from tlab_analysis import trpl


def create_figure(item_to_data: dict[str, trpl.TRPLData]) -> go.Figure:
    return (
        go.Figure(
            [
                go.Surface(
                    z=data.to_streak_image(),
                    x=data.wavelength.unique(),
                    y=data.time.unique(),
                    name=key,
                )
                for key, data in item_to_data.items()
            ]
        )
        .update_traces(
            hovertemplate=""
            "Wavelength: %{x:.2f} nm<br>"
            "Time: %{y:.2f} ns<br>"
            "Intensity: %{z:d}<br>"
            "<extra></extra>"
        )
        .update_layout(
            scene=dict(
                xaxis_title="Wavelength (nm)",
                yaxis_title="Time (ns)",
                zaxis_title="Intensity (arb.units)",
                aspectmode="auto",
            ),
            margin=dict(l=40, r=40, b=20, t=10),
        )
        .update_traces(
            contours_x=dict(show=True, usecolormap=True, highlightcolor="cyan"),
            contours_y=dict(show=True, usecolormap=True, highlightcolor="cyan"),
            contours_z=dict(
                show=True, usecolormap=True, highlightcolor="limegreen", project_z=True
            ),
        )
    )

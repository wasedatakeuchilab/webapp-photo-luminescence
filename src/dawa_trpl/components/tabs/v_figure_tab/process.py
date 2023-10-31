from collections import abc

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_figure(dfs: abc.Iterable[pd.DataFrame], log_y: bool) -> go.Figure:
    dfs = [df.assign(name=df.attrs["filename"]) for df in dfs]
    df = pd.concat(dfs)
    range_y = np.array(
        [df["intensity"][np.isclose(df["time"], 0.0)].min(), df["intensity"].max()]
    )
    fig = (
        px.line(
            df,
            x="time",
            y="intensity",
            color="name",
            color_discrete_sequence=px.colors.qualitative.Set1,
            log_y=log_y,
        )
        .update_traces(
            hovertemplate=""
            "Time: %{x:.3g} ns<br>"
            "Intensity: %{y:.4g}<br>"
            "<extra></extra>"
        )
        .update_layout(
            legend=dict(font=dict(size=14), yanchor="top", y=-0.15, xanchor="left", x=0)
        )
        .update_xaxes(
            title_text="<b>Time (ns)</b>",
        )
        .update_yaxes(
            title_text="<b>Intensity (arb. units)</b>",
            range=(np.log10(range_y) if log_y else range_y) * [1.0, 1.05],
        )
    )
    return fig


def add_fitting_curve(fig: go.Figure, dfs: abc.Iterable[pd.DataFrame]) -> go.Figure:
    return fig.add_traces(
        [
            go.Scatter(
                x=df["time"],
                y=df["fit"],
                line=dict(color="black"),
                name=f"Double Exponential Approximation "
                f"a : b = {df.attrs['fit']['a']}:{df.attrs['fit']['b']}, "
                f"τ₁ = {df.attrs['fit']['tau1']:.3g} ns, "
                f"τ₂ = {df.attrs['fit']['tau2']:.3g} ns",
            )
            for df in dfs
            if "fit" in df.attrs
        ]
    )

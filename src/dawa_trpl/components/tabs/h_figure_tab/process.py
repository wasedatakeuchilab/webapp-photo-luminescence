import functools
import itertools
from collections import abc

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from tlab_analysis import utils


def create_figure(dfs: abc.Iterable[pd.DataFrame]) -> go.Figure:
    dfs = [df.assign(name=df.attrs["filename"]) for df in dfs]
    df = pd.concat(dfs)
    fig = (
        px.line(
            df,
            x="wavelength",
            y="intensity",
            color="name",
            color_discrete_sequence=px.colors.qualitative.Set1,
        )
        .update_traces(
            hovertemplate=""
            "Wavelength: %{x:.2f} nm<br>"
            "Intensity: %{y:.4g}<br>"
            "<extra></extra>"
        )
        .update_layout(
            legend=dict(font=dict(size=14), yanchor="top", y=-0.1, xanchor="left", x=0),
        )
        .update_xaxes(title_text="<b>Wavelength (nm)</b>")
        .update_yaxes(
            title_text="<b>Intensity (arb. units)</b>",
            range=(0, df["intensity"].max() * 1.05),
        )
    )
    return fig


def add_peak_vline(fig: go.Figure, dfs: abc.Iterable[pd.DataFrame]) -> go.Figure:
    def _add_peak_vline(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
        peaks = utils.find_peaks(
            df["wavelength"].to_list(),
            df["intensity"].to_list(),
        )
        for peak in peaks:
            fig.add_vline(
                peak.x,
                annotation=dict(
                    text=f"{peak.x:.2f} nm",
                    hovertext=f"Intensity: {peak.y:.4g}",
                ),
            )
        return fig

    return functools.reduce(_add_peak_vline, dfs, fig)


def add_FWHM_range(fig: go.Figure, dfs: abc.Iterable[pd.DataFrame]) -> go.Figure:
    def _add_FWHM_range(fig: go.Figure, df: pd.DataFrame, color: str) -> go.Figure:
        peaks = utils.find_peaks(
            df["wavelength"].to_list(),
            df["intensity"].to_list(),
        )
        for peak in peaks:
            fig.add_shape(
                type="line",
                label=go.layout.shape.Label(text=f"{peak.width:.1f}nm", yanchor="top"),
                x0=peak.x0,
                x1=peak.x1,
                y0=peak.y0,
                y1=peak.y0,
                showlegend=False,
                line=dict(dash="dash", color=color),
            )
        return fig
        # return fig.add_vrect(
        #     *half_range,
        #     fillcolor=fillcolor,
        #     opacity=0.10,
        #     annotation=dict(
        #         text=f"FWHM: {FWHM:.3g} nm",
        #         hovertext=""
        #         f"Left: {half_range[0]:.2f} nm<br>"
        #         f"Right: {half_range[1]:.2f} nm",
        #         xanchor="left",
        #     ),
        # )

    def _add_FWFM_range_wrapper(
        fig: go.Figure, df_and_color: tuple[pd.DataFrame, str]
    ) -> go.Figure:
        df, color = df_and_color
        return _add_FWHM_range(fig, df, color)

    return functools.reduce(
        _add_FWFM_range_wrapper,
        zip(dfs, itertools.cycle(px.colors.qualitative.Set1)),
        fig,
    )

import functools
import itertools
from collections import abc

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tlab_analysis.photo_luminescence as pl


def create_figure(trs: abc.Iterable[pl.TimeResolved]) -> go.Figure:
    df = pd.concat([tr.df for tr in trs])
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


def add_peak_vline(fig: go.Figure, trs: abc.Iterable[pl.TimeResolved]) -> go.Figure:
    def _add_peak_vline(fig: go.Figure, tr: pl.TimeResolved) -> go.Figure:
        return fig.add_vline(
            tr.peak_wavelength,
            annotation=dict(
                text=f"Wavelength: {tr.peak_wavelength:.2f} nm",
                hovertext=f"Intensity: {tr.peak_intensity:.4g}",
            ),
        )

    return functools.reduce(_add_peak_vline, trs, fig)


def add_FWHM_range(fig: go.Figure, trs: abc.Iterable[pl.TimeResolved]) -> go.Figure:
    def _add_FWHM_range(
        fig: go.Figure, tr: pl.TimeResolved, fillcolor: str
    ) -> go.Figure:
        return fig.add_vrect(
            *tr.half_range,
            fillcolor=fillcolor,
            opacity=0.10,
            annotation=dict(
                text=f"FWHM: {tr.FWHM:.3g} nm",
                hovertext=""
                f"Left: {tr.half_range[0]:.2f} nm<br>"
                f"Right: {tr.half_range[1]:.2f} nm",
                xanchor="left",
            ),
        )

    def _add_FWFM_range_wrapper(
        fig: go.Figure, tr_and_color: tuple[pl.TimeResolved, str]
    ) -> go.Figure:
        tr, fillcolor = tr_and_color
        return _add_FWHM_range(fig, tr, fillcolor)

    return functools.reduce(
        _add_FWFM_range_wrapper,
        zip(trs, itertools.cycle(px.colors.qualitative.Set1)),
        fig,
    )

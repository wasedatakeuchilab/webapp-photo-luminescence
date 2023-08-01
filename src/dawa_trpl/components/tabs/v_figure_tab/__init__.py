import os
import typing as t
from collections import abc

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc

from dawa_trpl import data_system as ds
from dawa_trpl.components import upload_bar
from dawa_trpl.components.tabs import common
from dawa_trpl.components.tabs.v_figure_tab import process

wavelength_slider = dcc.RangeSlider(
    id="v-wavelength-slider",
    min=0,
    max=800,
    value=(0, 800),
    step=1,
    marks=None,
    tooltip={"placement": "bottom", "always_visible": True},
)
fitting_curve_switch = dbc.Switch(
    id="v-fitting-curve-switch", label="Fitting", value=True, className="mt-2"
)
log_intensity_switch = dbc.Switch(
    id="v-log-intensity-switch", label="Log Intensity", value=True
)
normalize_intensity_switch = dbc.Switch(
    id="v-normalize-intensity-switch", label="Normalize Intensity", value=False
)
download = dcc.Download(id="v-csv-download")
download_button = dbc.Button(["Download CSV", download], id="v-csv-download-button")
graph = common.create_graph(id="v-figure-graph")
options = common.create_options_layout(
    options_components=[
        dbc.Label("Wavelength Range"),
        wavelength_slider,
        fitting_curve_switch,
        log_intensity_switch,
        normalize_intensity_switch,
    ],
    download_components=[download_button],
)
table = common.create_table(id="v-table")
layout = common.create_layout(graph, options, table)


@dash.callback(
    dash.Output(graph, "figure"),
    dash.Input(upload_bar.files_dropdown, "value"),
    dash.State(upload_bar.upload_dir_store, "data"),
    dash.Input(wavelength_slider, "value"),
    dash.Input(fitting_curve_switch, "value"),
    dash.Input(log_intensity_switch, "value"),
    dash.Input(normalize_intensity_switch, "value"),
    prevent_initial_call=True,
)
def update_graph(
    selected_items: list[str] | None,
    upload_dir: str | None,
    wavelength_range: list[int],
    fitting: bool,
    log_y: bool,
    normalize_intensity: bool,
) -> go.Figure:
    if not selected_items:
        return go.Figure()
    filepaths = ds.get_existing_item_filepaths(
        selected_items,
        ds.validate_upload_dir(upload_dir),
    )
    dfs = ds.load_time_dfs(
        filepaths,
        (
            float(wavelength_range[0]),
            float(wavelength_range[1]),
        ),  # TODO: Any other way to pass mypy?
        fitting,
        normalize_intensity,
    )
    fig = process.create_figure(dfs, log_y)
    if fitting:
        fig = process.add_fitting_curve(fig, dfs)
    return fig


@dash.callback(
    dash.Output(table, "data"),
    dash.Input(upload_bar.files_dropdown, "value"),
    dash.State(upload_bar.upload_dir_store, "data"),
    dash.Input(wavelength_slider, "value"),
    dash.Input(fitting_curve_switch, "value"),
    dash.Input(normalize_intensity_switch, "value"),
    prevent_initial_call=True,
)
def update_table(
    selected_items: list[str] | None,
    upload_dir: str | None,
    wavelength_range: list[int],
    fitting: bool,
    normalize_intensity: bool,
) -> list[dict[abc.Hashable, t.Any]] | None:
    if not selected_items:
        return None
    filepaths = ds.get_existing_item_filepaths(
        selected_items,
        ds.validate_upload_dir(upload_dir),
    )
    dfs = ds.load_time_dfs(
        filepaths,
        (
            float(wavelength_range[0]),
            float(wavelength_range[1]),
        ),  # TODO: Any other way to pass mypy?
        fitting,
        normalize_intensity,
    )
    df = pd.concat(dfs)
    return df.to_dict("records")


@dash.callback(
    dash.Output(wavelength_slider, "min"),
    dash.Output(wavelength_slider, "max"),
    dash.Input(upload_bar.files_dropdown, "value"),
    dash.State(upload_bar.upload_dir_store, "data"),
    prevent_initial_call=True,
)
def update_wavelength_slider_range(
    selected_items: list[str] | None, upload_dir: str | None
) -> tuple[float, float]:
    if not selected_items:
        raise dash.exceptions.PreventUpdate
    filepaths = ds.get_existing_item_filepaths(
        selected_items,
        ds.validate_upload_dir(upload_dir),
    )
    wavelength = np.concatenate(
        [ds.load_trpl_data(filepath).wavelength for filepath in filepaths]
    )
    return int(wavelength.min()), int(wavelength.max())


@dash.callback(
    dash.Output(download_button, "disabled"),
    dash.Input(upload_bar.files_dropdown, "value"),
)
def update_download_button_ability(selected_items: list[str] | None) -> bool:
    if selected_items is None:
        return True
    return bool(len(selected_items) != 1)


@dash.callback(
    dash.Output(download, "data"),
    dash.Input(download_button, "n_clicks"),
    dash.State(upload_bar.files_dropdown, "value"),
    dash.State(upload_bar.upload_dir_store, "data"),
    dash.State(wavelength_slider, "value"),
    dash.State(fitting_curve_switch, "value"),
    dash.State(normalize_intensity_switch, "value"),
    prevent_initial_call=True,
)
def download_csv(
    n_clicks: int,
    selected_items: list[str] | None,
    upload_dir: str | None,
    wavelength_range: list[int],
    fitting: bool,
    normalize_intensity: bool,
) -> dict[str, t.Any]:
    if not selected_items:
        raise dash.exceptions.PreventUpdate  # TODO: Notify error to users
    filepaths = ds.get_existing_item_filepaths(
        selected_items,
        ds.validate_upload_dir(upload_dir),
    )
    if len(filepaths) == 0:
        raise dash.exceptions.PreventUpdate  # TODO: Notify error to users
    filepath = filepaths[0]
    df = ds.load_wavelength_df(
        filepath, tuple(wavelength_range[:2]), fitting, normalize_intensity
    )
    filename = (
        f"v({wavelength_range[0]}-{wavelength_range[1]})-"
        + os.path.basename(filepath)
        + ".csv"
    )
    return dict(
        filename=filename,
        content=df.to_csv(index=False),
        type="text/csv",
        base64=False,
    )

import os
import typing as t
from collections import abc

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import dcc

from webapp_photo_luminescence import data_system as ds
from webapp_photo_luminescence.components import upload_bar
from webapp_photo_luminescence.components.tabs import common
from webapp_photo_luminescence.components.tabs.h_figure_tab import process

peak_vline_switch = dbc.Switch(
    id="h-peak-vline-switch", label="Vertical Line at Peak", value=False
)
FWHM_range_switch = dbc.Switch(
    id="h-FWHM-range-switch", label="FWHM Range", value=False
)
normalize_intensity_switch = dbc.Switch(
    id="h-normalize-intensity-switch", label="Normalize Intensity", value=False
)
download = dcc.Download(id="h-csv-download")
download_button = dbc.Button(
    ["Download CSV", download], id="h-csv-download-button", disabled=True
)
graph = common.create_graph(id="h-figure-graph")
options = common.create_options_layout(
    options_components=[
        peak_vline_switch,
        FWHM_range_switch,
        normalize_intensity_switch,
    ],
    download_components=[download_button],
)
table = common.create_table(id="h-table")
layout = common.create_layout(graph, options, table)


@dash.callback(
    dash.Output(graph, "figure"),
    dash.Input(upload_bar.files_dropdown, "value"),
    dash.State(upload_bar.upload_dir_store, "data"),
    dash.Input(peak_vline_switch, "value"),
    dash.Input(FWHM_range_switch, "value"),
    dash.Input(normalize_intensity_switch, "value"),
    prevent_initial_call=True,
)
def update_graph(
    selected_items: list[str] | None,
    upload_dir: str | None,
    show_peak_vline: bool,
    show_FWHM_range: bool,
    normalize_intensity: bool,
) -> go.Figure:
    if not selected_items:
        return go.Figure()
    filepaths = ds.get_existing_item_filepaths(
        selected_items,
        ds.validate_upload_dir(upload_dir),
    )
    trs = ds.load_time_resolveds(filepaths, normalize_intensity)
    fig = process.create_figure(trs)
    if show_peak_vline:
        fig = process.add_peak_vline(fig, trs)
    if show_FWHM_range:
        fig = process.add_FWHM_range(fig, trs)
    return fig


@dash.callback(
    dash.Output(table, "data"),
    dash.Input(upload_bar.files_dropdown, "value"),
    dash.State(upload_bar.upload_dir_store, "data"),
    dash.Input(normalize_intensity_switch, "value"),
    prevent_initial_call=True,
)
def update_table(
    selected_items: list[str] | None, upload_dir: str | None, normalize_intensity: bool
) -> list[dict[abc.Hashable, t.Any]] | None:
    if not selected_items:
        return None
    filepaths = ds.get_existing_item_filepaths(
        selected_items,
        ds.validate_upload_dir(upload_dir),
    )
    trs = ds.load_time_resolveds(filepaths, normalize_intensity)
    df = pd.concat([tr.df for tr in trs])
    return df.to_dict("records")


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
    dash.State(normalize_intensity_switch, "value"),
    prevent_initial_call=True,
)
def download_csv(
    n_clicks: int,
    selected_items: list[str] | None,
    upload_dir: str | None,
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
    tr = ds.load_time_resolved(filepath, normalize_intensity)
    return dict(
        filename="h-" + os.path.basename(filepath) + ".csv",
        content=tr.df.to_csv(index=False),
        type="text/csv",
        base64=False,
    )

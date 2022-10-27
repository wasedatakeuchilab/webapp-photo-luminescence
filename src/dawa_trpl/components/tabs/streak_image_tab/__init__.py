import base64
import os
import typing as t

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc

from dawa_trpl import data_system as ds
from dawa_trpl.components import upload_bar
from dawa_trpl.components.tabs import common
from dawa_trpl.components.tabs.streak_image_tab import process

img_download = dcc.Download("img-download")
img_download_button = dbc.Button(
    ["Download Image", img_download],
    id="img-download-button",
    color="primary",
    className="mt-2",
    disabled=True,
)
graph = common.create_graph(id="streak-image-graph")
options = common.create_options_layout(
    options_components=None, download_components=[img_download_button]
)
layout = common.create_layout(graph, options)


@dash.callback(
    dash.Output(graph, "figure"),
    dash.Input(upload_bar.files_dropdown, "value"),
    dash.State(upload_bar.upload_dir_store, "data"),
    prevent_initial_call=True,
)
def update_streak_image(
    selected_items: list[str] | None,
    upload_dir: str | None,
) -> go.Figure:
    if not selected_items:
        return go.Figure()
    filepaths = ds.get_existing_item_filepaths(
        selected_items,
        ds.validate_upload_dir(upload_dir),
    )
    item_to_data = {
        os.path.basename(filepath): ds.load_pldata(filepath) for filepath in filepaths
    }
    fig = process.create_figure(item_to_data)
    return fig


@dash.callback(
    dash.Output(img_download_button, "disabled"),
    dash.Input(upload_bar.files_dropdown, "value"),
)
def update_download_button_ability(selected_items: list[str] | None) -> bool:
    if not selected_items:
        return True
    return bool(len(selected_items) != 1)


@dash.callback(
    dash.Output(img_download, "data"),
    dash.Input(img_download_button, "n_clicks"),
    dash.State(upload_bar.files_dropdown, "value"),
    dash.State(upload_bar.upload_dir_store, "data"),
    prevent_initial_call=True,
)
def download_img(
    n_clicks: int | None,
    selected_items: list[str] | None,
    upload_dir: str | None,
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
    data = ds.load_pldata(filepath)
    return dict(
        filename=os.path.basename(filepath),
        content=base64.urlsafe_b64encode(data.to_raw_binary()).decode(),
        type="application/octet-stream",
        base64=True,
    )

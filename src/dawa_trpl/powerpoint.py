import base64
import datetime
import io
import pathlib
import re
import typing as t

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import tlab_pptx
from dash import dcc
from tlab_analysis import utils

from dawa_trpl import data_system as ds
from dawa_trpl.components import upload_bar
from dawa_trpl.components.tabs import h_figure_tab, v_figure_tab

download = dcc.Download("pptx-download")
download_button = dbc.Button(
    ["Download PowerPoint", download],
    id="pptx-download-button",
    disabled=True,
    color="primary",
    className="mt-2",
)
datepicker = dcc.DatePickerSingle(
    id="experiment-date-picker-single", with_portal=True, persistence_type="session"
)


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
    dash.State(v_figure_tab.wavelength_slider, "value"),
    dash.State(h_figure_tab.graph, "figure"),
    dash.State(v_figure_tab.graph, "figure"),
    dash.State(datepicker, "date"),
    prevent_initial_call=True,
)
def download_powerpoint(
    n_clicks: int,
    selected_items: list[str] | None,
    upload_dir: str,
    wavelength_range: list[int],
    h_fig: dict[str, t.Any] | None,
    v_fig: dict[str, t.Any] | None,
    experiment_date: str | None,
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
    data = ds.load_trpl_data(filepath)
    frame = (
        int(match[0])
        if (match := re.search("(?<=Frame=)[0-9]+(?=,)", "".join(data.metadata)))
        else 0
    )
    wdf = ds.load_wavelength_df(filepath)
    tdf = ds.load_time_df(filepath, tuple(wavelength_range[:2]), fitting=True)
    prs = tlab_pptx.presentation.photo_luminescence.build(
        title_text="title",
        excitation_wavelength=405,  # TODO: Retrieve from `item`
        excitation_power=5,  # TODO: Retrieve from `item`
        time_range=round(data.time.max() - data.time.min()),
        center_wavelength=utils.find_peak(
            wdf["wavelength"].to_list(),
            wdf["smoothed_intensity"].to_list(),
        )[0],
        FWHM=utils.find_FWHM(
            wdf["wavelength"].to_list(),
            wdf["smoothed_intensity"].to_list(),
        ),
        frame=frame,
        date=datetime.date.fromisoformat(experiment_date)
        if experiment_date
        else datetime.date.today(),
        h_fig=go.Figure(h_fig),
        v_fig=go.Figure(v_fig),
        a=int(tdf.attrs["fit"]["a"]),
        b=int(tdf.attrs["fit"]["b"]),
        tau1=float(tdf.attrs["fit"]["tau1"]),
        tau2=float(tdf.attrs["fit"]["tau2"]),
    )
    with io.BytesIO() as f:
        prs.save(f)
        f.seek(0)
        raw = f.read()
    return dict(
        filename=pathlib.Path(filepath).with_suffix(".pptx").name,
        content=base64.urlsafe_b64encode(raw).decode(),
        type="application/octet-stream",
        base64=True,
    )

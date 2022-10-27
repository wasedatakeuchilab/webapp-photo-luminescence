import base64
import os
import pathlib
import tempfile

import dash
import dash_bootstrap_components as dbc
from dash import dcc

from dawa_trpl import config
from dawa_trpl import data_system as ds

upload_button = dbc.Button(
    "Upload Files", id="upload-button", color="primary", className="my-2"
)
files_dropdown = dcc.Dropdown(
    id="uploaded-files-dropdown",
    options=[],
    value=None,
    multi=True,
    clearable=False,
    className="mt-3 w-100",
)
file_uploader = dcc.Upload([upload_button], multiple=True)
upload_dir_store = dcc.Store(id="upload-dir-store", storage_type="session", data="")
last_uploaded_store = dcc.Store(
    id="last-upload-store", storage_type="memory", data=list()
)
layout = dbc.Row(
    [
        dbc.Col(files_dropdown),
        dbc.Col(file_uploader, width="auto"),
        upload_dir_store,
        last_uploaded_store,
    ],
    id="uploadbar-row",
    className="frex-nowrap ms-auto",
    style={"width": "100%"},
)


@dash.callback(
    dash.Output(upload_dir_store, "data"), dash.Input(upload_dir_store, "data")
)
def update_upload_dir(upload_dir: str | None) -> str:
    if upload_dir:
        raise dash.exceptions.PreventUpdate
    if not os.path.exists(config.UPLOAD_BASEDIR):  # pragma: no cover
        os.mkdir(config.UPLOAD_BASEDIR)
    tmpdir = tempfile.mkdtemp(dir=config.UPLOAD_BASEDIR)
    return tmpdir


@dash.callback(
    dash.Output(last_uploaded_store, "data"),
    dash.Input(file_uploader, "contents"),
    dash.State(file_uploader, "filename"),
    dash.State(upload_dir_store, "data"),
    prevent_initial_call=True,
)
def on_upload_files(
    contents: list[str] | None, filenames: list[str] | None, upload_dir: str | None
) -> list[str]:
    upload_dir = ds.validate_upload_dir(upload_dir)
    if contents is None or filenames is None:
        raise dash.exceptions.PreventUpdate  # TODO: Notify error to users
    for filename, content in zip(filenames, contents):
        with open(os.path.join(upload_dir, filename), "wb") as f:
            content_type, content_string = content.split(",")
            f.write(base64.urlsafe_b64decode(content_string))
    return filenames


@dash.callback(
    dash.Output(files_dropdown, "options"),
    dash.Input(last_uploaded_store, "data"),
    dash.State(upload_dir_store, "data"),
    prevent_initial_call=True,
)
def update_dropdown_options(
    last_uploaded_files: list[str] | None, upload_dir: str | None
) -> list[str]:
    upload_dir = ds.validate_upload_dir(upload_dir)
    return [path.name for path in pathlib.Path(upload_dir).iterdir() if path.is_file()]


@dash.callback(
    dash.Output(files_dropdown, "value"),
    dash.Input(last_uploaded_store, "data"),
    dash.State(files_dropdown, "value"),
    prevent_initial_call=True,
)
def update_dropdown_value(
    filenames: list[str] | None, current_value: list[str] | None
) -> list[str]:
    if current_value is None:
        current_value = list()
    if filenames is None:
        filenames = list()
    return current_value + filenames

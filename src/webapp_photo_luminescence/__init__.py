__version__ = "0.4.0"

import pathlib

import dash
import dash_bootstrap_components as dbc

from . import config, powerpoint
from .components import tabs, upload_bar

app = dash.Dash(
    __name__,
    title="PL Analysis",
    url_base_pathname=config.URL_BASE_PATH,
    external_stylesheets=[dbc.themes.MATERIA],
    extra_hot_reload_paths=list(pathlib.Path(__file__).parent.glob("**/*.py")),
    suppress_callback_exceptions=True,
)

server = app.server

navbar = dbc.Navbar(
    [
        dbc.NavbarBrand(
            [
                "Photo Luminescence ",
                dash.html.Small("v" + __version__),
            ],
            href="/",
        )
    ],
    color="dark",
    dark=True,
    style={"height": "5vh"},
)

sidebar = dash.html.Div(
    [
        dbc.Row(
            [
                dbc.Col([]),
            ],
            style={"height": "70vh"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dash.html.H5("Power Point"),
                        dash.html.Label("Experiment Date", className="me-2"),
                        powerpoint.datepicker,
                        powerpoint.download_button,
                    ]
                ),
            ],
            style={"height": "30vh"},
        ),
    ]
)

main_container = layout = dbc.Container(
    [
        dbc.Row([dbc.Col(upload_bar.layout)]),
        dbc.Row([dbc.Col(tabs.layout)]),
    ],
    fluid=True,
)

app.layout = dbc.Container(
    [
        dbc.Row([navbar]),
        dbc.Row(
            [
                dbc.Col(sidebar, width=2, class_name="bg-light"),
                dbc.Col(main_container, width=10),
            ],
            style={"height": "100vh"},
        ),
    ],
    fluid=True,
)

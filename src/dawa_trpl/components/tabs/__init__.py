import dash_bootstrap_components as dbc

from . import h_figure_tab, streak_image_tab, v_figure_tab

layout = dbc.Tabs(
    [
        dbc.Tab(
            streak_image_tab.layout,
            id="streak-image-tab",
            label="Streak Image",
        ),
        dbc.Tab(
            h_figure_tab.layout,
            id="h-figure-tab",
            label="H-Figure",
        ),
        dbc.Tab(
            v_figure_tab.layout,
            id="v-figure-tab",
            label="V-Figure",
        ),
    ],
    id="figure-tabs",
    className="nav-fill",
)

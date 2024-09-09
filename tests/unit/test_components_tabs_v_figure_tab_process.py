import pathlib

import pandas as pd
import plotly.graph_objects as go
import pytest

from dawa_trpl import data_system as ds
from dawa_trpl.components.tabs.v_figure_tab import process
from tests import IMGDIR


@pytest.fixture(scope="module")
def dfs() -> list[pd.DataFrame]:
    def load_time_df(filepath: pathlib.Path) -> pd.DataFrame:
        df = ds.load_time_df(filepath.as_posix())
        return df

    return list(map(load_time_df, IMGDIR.glob("*.img")))


@pytest.mark.parametrize("log_y", [True, False])
def test_create_figure(dfs: list[pd.DataFrame], log_y: bool) -> None:
    fig = process.create_figure(dfs, log_y)
    assert isinstance(fig, go.Figure)


def test_add_fitting_curve(dfs: list[pd.DataFrame]) -> None:
    fig = process.add_fitting_curve(go.Figure(), dfs)
    assert isinstance(fig, go.Figure)

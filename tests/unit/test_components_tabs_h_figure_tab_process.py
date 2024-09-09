import pathlib

import pandas as pd
import plotly.graph_objects as go
import pytest

from dawa_trpl import data_system as ds
from dawa_trpl.components.tabs.h_figure_tab import process
from tests import IMGDIR


@pytest.fixture(scope="module")
def dfs() -> list[pd.DataFrame]:
    def load_wavelength_df(filepath: pathlib.Path) -> pd.DataFrame:
        df = ds.load_wavelength_df(filepath.as_posix())
        return df

    return list(map(load_wavelength_df, IMGDIR.glob("*.img")))


def test_create_figure(dfs: list[pd.DataFrame]) -> None:
    fig = process.create_figure(dfs)
    assert isinstance(fig, go.Figure)


def test_add_peak_vline(dfs: list[pd.DataFrame]) -> None:
    fig = process.add_peak_vline(go.Figure(), dfs)
    assert isinstance(fig, go.Figure)


def test_add_FWHM_range(dfs: list[pd.DataFrame]) -> None:
    fig = process.add_FWHM_range(go.Figure(), dfs)
    assert isinstance(fig, go.Figure)

import pathlib

import plotly.graph_objects as go
import pytest
import tlab_analysis.photo_luminescence as pl

from dawa_trpl.components.tabs.h_figure_tab import process
from tests import IMGDIR


@pytest.fixture(scope="module")
def trs() -> list[pl.TimeResolved]:
    def load_time_resolved(filepath: pathlib.Path) -> pl.TimeResolved:
        tr = pl.read_img(filepath).resolve_along_time()
        tr.df["name"] = filepath.name
        return tr

    return list(map(load_time_resolved, IMGDIR.glob("*.img")))


def test_create_figure(trs: list[pl.TimeResolved]) -> None:
    fig = process.create_figure(trs)
    assert isinstance(fig, go.Figure)


def test_add_peak_vline(trs: list[pl.TimeResolved]) -> None:
    fig = process.add_peak_vline(go.Figure(), trs)
    assert isinstance(fig, go.Figure)


def test_add_FWHM_range(trs: list[pl.TimeResolved]) -> None:
    fig = process.add_FWHM_range(go.Figure(), trs)
    assert isinstance(fig, go.Figure)

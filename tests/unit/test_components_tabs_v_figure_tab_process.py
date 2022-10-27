import pathlib

import plotly.graph_objects as go
import pytest
import tlab_analysis.photo_luminescence as pl

from dawa_trpl import data_system as ds
from dawa_trpl.components.tabs.v_figure_tab import process
from tests import IMGDIR


@pytest.fixture(scope="module")
def wrs() -> list[pl.WavelengthResolved]:
    def load_wavelength_resolved(filepath: pathlib.Path) -> pl.WavelengthResolved:
        wr = ds.load_wavelength_resolved(filepath.as_posix())
        return wr

    return list(map(load_wavelength_resolved, IMGDIR.glob("*.img")))


@pytest.mark.parametrize("log_y", [True, False])
def test_create_figure(wrs: list[pl.WavelengthResolved], log_y: bool) -> None:
    fig = process.create_figure(wrs, log_y)
    assert isinstance(fig, go.Figure)


def test_add_fitting_curve(wrs: list[pl.WavelengthResolved]) -> None:
    fig = process.add_fitting_curve(go.Figure(), wrs)
    assert isinstance(fig, go.Figure)

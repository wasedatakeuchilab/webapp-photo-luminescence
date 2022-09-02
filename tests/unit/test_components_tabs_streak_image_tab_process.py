import plotly.graph_objects as go
import pytest
import tlab_analysis.photo_luminescence as pl

from tests import IMGDIR
from webapp_photo_luminescence.components.tabs.streak_image_tab import process


@pytest.fixture()
def item_to_data() -> dict[str, pl.Data]:
    return {filepath.name: pl.read_img(filepath) for filepath in IMGDIR.glob("*.img")}


def test_create_figure(item_to_data: dict[str, pl.Data]) -> None:
    fig = process.create_figure(item_to_data)
    assert isinstance(fig, go.Figure)

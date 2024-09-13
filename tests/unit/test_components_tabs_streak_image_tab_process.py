import plotly.graph_objects as go
import pytest
from tlab_analysis import trpl

from dawa_trpl.components.tabs.streak_image_tab import process
from tests import IMGDIR


@pytest.fixture()
def item_to_data() -> dict[str, trpl.TRPLData]:
    return {
        filepath.name: trpl.read_file(filepath) for filepath in IMGDIR.glob("*.img")
    }


def test_create_figure(item_to_data: dict[str, trpl.TRPLData]) -> None:
    fig = process.create_figure(item_to_data)
    assert isinstance(fig, go.Figure)

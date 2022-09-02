import os
from collections import abc
from unittest import mock

import dash
import pandas as pd
import plotly.graph_objects as go
import pytest
import tlab_analysis.photo_luminescence as pl

from tests import IMGDIR
from webapp_photo_luminescence.components.tabs import h_figure_tab


@pytest.fixture()
def selected_items() -> list[str]:
    return ["item.img"]


@pytest.fixture(scope="module")
def trs() -> list[pl.TimeResolved]:
    return [
        pl.read_img(filepath).resolve_along_time() for filepath in IMGDIR.glob("*.img")
    ]


@pytest.fixture()
def process_mock() -> abc.Generator[mock.Mock, None, None]:
    with mock.patch(
        "webapp_photo_luminescence.components.tabs.h_figure_tab.process"
    ) as m:
        yield m


@pytest.fixture()
def ds_mock(
    trs: list[pl.TimeResolved],
    selected_items: list[str],
    upload_dir: str,
) -> abc.Generator[mock.Mock, None, None]:
    with mock.patch("webapp_photo_luminescence.components.tabs.h_figure_tab.ds") as m:
        m.load_time_resolveds.return_value = trs
        m.get_existing_item_filepaths.return_value = [
            os.path.join(upload_dir, item) for item in selected_items
        ]
        yield m


@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_update_graph_when_items_are_selected(
    process_mock: mock.Mock,
    ds_mock: mock.Mock,
    selected_items: list[str] | None,
    upload_dir: str,
    normalize_intensity: bool,
) -> None:
    fig = h_figure_tab.update_graph(
        selected_items,
        upload_dir,
        show_peak_vline=False,
        show_FWHM_range=False,
        normalize_intensity=normalize_intensity,
    )
    assert fig == process_mock.create_figure.return_value
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    ds_mock.load_time_resolveds.assert_called_once_with(
        ds_mock.get_existing_item_filepaths.return_value,
        normalize_intensity,
    )
    process_mock.create_figure.assert_called_once_with(
        ds_mock.load_time_resolveds.return_value
    )


@pytest.mark.parametrize("selected_items", [list(), None])
def test_update_graph_when_selected_items_is_empty_or_None(
    selected_items: list[str] | None,
    upload_dir: str,
) -> None:
    fig = h_figure_tab.update_graph(
        selected_items,
        upload_dir,
        show_peak_vline=False,
        show_FWHM_range=False,
        normalize_intensity=False,
    )
    assert fig == go.Figure()


@pytest.mark.parametrize("show_peak_vline", [True, False])
def test_update_graph_with_show_peak_vline(
    process_mock: mock.Mock,
    ds_mock: mock.Mock,
    selected_items: list[str],
    upload_dir: str,
    show_peak_vline: bool,
) -> None:
    fig = h_figure_tab.update_graph(
        selected_items,
        upload_dir,
        show_peak_vline=show_peak_vline,
        show_FWHM_range=False,
        normalize_intensity=False,
    )
    if show_peak_vline:
        assert fig == process_mock.add_peak_vline.return_value
        process_mock.add_peak_vline.assert_called_once_with(
            process_mock.create_figure.return_value,
            ds_mock.load_time_resolveds.return_value,
        )
    else:
        assert fig == process_mock.create_figure.return_value
        process_mock.add_peak_vline.assert_not_called()


@pytest.mark.parametrize("show_FWHM_range", [True, False])
def test_update_graph_with_show_FWHM_range(
    process_mock: mock.Mock,
    ds_mock: mock.Mock,
    selected_items: list[str],
    upload_dir: str,
    show_FWHM_range: bool,
) -> None:
    fig = h_figure_tab.update_graph(
        selected_items,
        upload_dir,
        show_peak_vline=False,
        show_FWHM_range=show_FWHM_range,
        normalize_intensity=False,
    )
    if show_FWHM_range:
        assert fig == process_mock.add_FWHM_range.return_value
        process_mock.add_FWHM_range.assert_called_once_with(
            process_mock.create_figure.return_value,
            ds_mock.load_time_resolveds.return_value,
        )
    else:
        assert fig == process_mock.create_figure.return_value
        process_mock.add_FWHM_range.assert_not_called()


@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_update_table_when_items_are_selected(
    ds_mock: mock.Mock,
    selected_items: list[str],
    upload_dir: str,
    normalize_intensity: bool,
) -> None:
    table = h_figure_tab.update_table(
        selected_items,
        upload_dir,
        normalize_intensity,
    )
    assert table == pd.concat(
        [tr.df for tr in ds_mock.load_time_resolveds.return_value]
    ).to_dict("records")
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    ds_mock.load_time_resolveds.assert_called_once_with(
        ds_mock.get_existing_item_filepaths.return_value,
        normalize_intensity,
    )


@pytest.mark.parametrize("selected_items", [list(), None])
def test_update_table_when_selected_items_is_empty_or_None(
    selected_items: list[str] | None,
    upload_dir: str,
) -> None:
    table = h_figure_tab.update_table(
        selected_items,
        upload_dir,
        normalize_intensity=False,
    )
    assert table is None


@pytest.mark.parametrize("selected_items", [list(), None])
def test_update_download_button_ability_when_no_item_is_selected(
    selected_items: list[str] | None,
) -> None:
    assert h_figure_tab.update_download_button_ability(selected_items)


def test_update_download_button_ability_when_one_item_is_selected(
    selected_items: list[str],
) -> None:
    assert not h_figure_tab.update_download_button_ability(selected_items)


@pytest.mark.parametrize(
    "selected_items", [[f"item{i}.img" for i in range(j)] for j in range(2, 5)]
)
def test_update_download_button_ability_when_multiple_items_are_selected(
    selected_items: list[str],
) -> None:
    assert h_figure_tab.update_download_button_ability(selected_items)


@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_download_csv(
    ds_mock: mock.Mock,
    selected_items: list[str],
    upload_dir: str,
    normalize_intensity: bool,
) -> None:
    assert h_figure_tab.download_csv(
        1, selected_items, upload_dir, normalize_intensity
    ) == dict(
        filename="h-" + selected_items[0] + ".csv",
        content=ds_mock.load_time_resolved.return_value.df.to_csv.return_value,
        type="text/csv",
        base64=False,
    )
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    ds_mock.load_time_resolved.assert_called_once_with(
        ds_mock.get_existing_item_filepaths.return_value[0],
        normalize_intensity,
    )


@pytest.mark.parametrize("selected_items", [list(), None])
def test_download_csv_when_no_item_is_selected(
    selected_items: list[str],
    upload_dir: str,
) -> None:
    with pytest.raises(dash.exceptions.PreventUpdate):
        h_figure_tab.download_csv(
            1, selected_items, upload_dir, normalize_intensity=False
        )


def test_download_csv_when_selected_item_does_not_exist(
    ds_mock: mock.Mock,
    selected_items: list[str],
    upload_dir: str,
) -> None:
    ds_mock.get_existing_item_filepaths.return_value = list()
    with pytest.raises(dash.exceptions.PreventUpdate):
        h_figure_tab.download_csv(
            1, selected_items, upload_dir, normalize_intensity=False
        )

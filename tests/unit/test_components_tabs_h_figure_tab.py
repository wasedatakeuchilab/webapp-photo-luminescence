import os

import dash
import pandas as pd
import plotly.graph_objects as go
import pytest
import pytest_mock
from tlab_analysis import trpl

from dawa_trpl.components.tabs import h_figure_tab
from tests import IMGDIR


@pytest.fixture()
def selected_items() -> list[str]:
    return ["item.img"]


@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_update_graph_when_items_are_selected(
    selected_items: list[str] | None,
    upload_dir: str,
    normalize_intensity: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    process_mock = mocker.patch("dawa_trpl.components.tabs.h_figure_tab.process")
    ds_mock = mocker.patch("dawa_trpl.components.tabs.h_figure_tab.ds")
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
    ds_mock.load_wavelength_dfs.assert_called_once_with(
        ds_mock.get_existing_item_filepaths.return_value,
        normalize_intensity,
    )
    process_mock.create_figure.assert_called_once_with(
        ds_mock.load_wavelength_dfs.return_value
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
    selected_items: list[str],
    upload_dir: str,
    show_peak_vline: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    process_mock = mocker.patch("dawa_trpl.components.tabs.h_figure_tab.process")
    ds_mock = mocker.patch("dawa_trpl.components.tabs.h_figure_tab.ds")
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
            ds_mock.load_wavelength_dfs.return_value,
        )
    else:
        assert fig == process_mock.create_figure.return_value
        process_mock.add_peak_vline.assert_not_called()


@pytest.mark.parametrize("show_FWHM_range", [True, False])
def test_update_graph_with_show_FWHM_range(
    selected_items: list[str],
    upload_dir: str,
    show_FWHM_range: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    process_mock = mocker.patch("dawa_trpl.components.tabs.h_figure_tab.process")
    ds_mock = mocker.patch("dawa_trpl.components.tabs.h_figure_tab.ds")
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
            ds_mock.load_wavelength_dfs.return_value,
        )
    else:
        assert fig == process_mock.create_figure.return_value
        process_mock.add_FWHM_range.assert_not_called()


@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_update_table_when_items_are_selected(
    selected_items: list[str],
    upload_dir: str,
    normalize_intensity: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    ds_mock = mocker.patch("dawa_trpl.components.tabs.h_figure_tab.ds")
    ds_mock.load_wavelength_dfs.return_value = [
        trpl.read_file(filepath).aggregate_along_time()
        for filepath in IMGDIR.glob("*.img")
    ]
    table = h_figure_tab.update_table(
        selected_items,
        upload_dir,
        normalize_intensity,
    )
    assert table == pd.concat(ds_mock.load_wavelength_dfs.return_value).to_dict(
        "records"
    )
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    ds_mock.load_wavelength_dfs.assert_called_once_with(
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
    selected_items: list[str],
    upload_dir: str,
    normalize_intensity: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    ds_mock = mocker.patch("dawa_trpl.components.tabs.h_figure_tab.ds")
    ds_mock.get_existing_item_filepaths.return_value = [
        os.path.join(upload_dir, item) for item in selected_items
    ]
    assert h_figure_tab.download_csv(
        1, selected_items, upload_dir, normalize_intensity
    ) == dict(
        filename="h-" + selected_items[0] + ".csv",
        content=ds_mock.load_wavelength_df.return_value.to_csv.return_value,
        type="text/csv",
        base64=False,
    )
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    ds_mock.load_wavelength_df.assert_called_once_with(
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
    selected_items: list[str],
    upload_dir: str,
    mocker: pytest_mock.MockerFixture,
) -> None:
    mocker.patch(
        "dawa_trpl.data_system.get_existing_item_filepaths", return_value=list()
    )
    with pytest.raises(dash.exceptions.PreventUpdate):
        h_figure_tab.download_csv(
            1, selected_items, upload_dir, normalize_intensity=False
        )

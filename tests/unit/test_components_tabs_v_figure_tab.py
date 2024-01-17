import os

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest
import pytest_mock
from dawa_trpl.components.tabs import v_figure_tab
from tlab_analysis import trpl

from tests import IMGDIR


@pytest.fixture()
def selected_items() -> list[str]:
    return ["item.img"]


@pytest.fixture()
def wavelength_range() -> list[int]:
    return [450, 500]


@pytest.mark.parametrize("log_y", [True, False])
@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_update_graph_when_items_are_selected(
    selected_items: list[str] | None,
    upload_dir: str,
    wavelength_range: list[int],
    log_y: bool,
    normalize_intensity: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    process_mock = mocker.patch("dawa_trpl.components.tabs.v_figure_tab.process")
    ds_mock = mocker.patch("dawa_trpl.components.tabs.v_figure_tab.ds")
    fig = v_figure_tab.update_graph(
        selected_items,
        upload_dir,
        wavelength_range,
        fitting=False,
        log_y=log_y,
        normalize_intensity=normalize_intensity,
    )
    assert fig == process_mock.create_figure.return_value
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    ds_mock.load_time_dfs.assert_called_once_with(
        ds_mock.get_existing_item_filepaths.return_value,
        tuple(wavelength_range),
        False,
        normalize_intensity,
    )
    process_mock.create_figure.assert_called_once_with(
        ds_mock.load_time_dfs.return_value,
        log_y,
    )


@pytest.mark.parametrize("selected_items", [list(), None])
def test_update_graph_when_selected_items_is_empty_or_None(
    selected_items: list[str] | None,
    upload_dir: str,
    wavelength_range: list[int],
) -> None:
    fig = v_figure_tab.update_graph(
        selected_items,
        upload_dir,
        wavelength_range,
        fitting=False,
        log_y=False,
        normalize_intensity=False,
    )
    assert fig == go.Figure()


@pytest.mark.parametrize("fitting", [True, False])
def test_update_graph_with_fitting(
    selected_items: list[str],
    upload_dir: str,
    wavelength_range: list[str],
    fitting: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    process_mock = mocker.patch("dawa_trpl.components.tabs.v_figure_tab.process")
    ds_mock = mocker.patch("dawa_trpl.components.tabs.v_figure_tab.ds")
    fig = v_figure_tab.update_graph(
        selected_items,
        upload_dir,
        wavelength_range,
        fitting=fitting,
        log_y=False,
        normalize_intensity=False,
    )
    if fitting:
        assert fig == process_mock.add_fitting_curve.return_value
        process_mock.add_fitting_curve.assert_called_once_with(
            process_mock.create_figure.return_value,
            ds_mock.load_time_dfs.return_value,
        )
    else:
        assert fig == process_mock.create_figure.return_value
        process_mock.add_fitting_curve.assert_not_called()


@pytest.mark.parametrize("fitting", [True, False])
@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_update_table_when_items_are_selected(
    selected_items: list[str],
    upload_dir: str,
    wavelength_range: list[int],
    fitting: bool,
    normalize_intensity: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    ds_mock = mocker.patch("dawa_trpl.components.tabs.v_figure_tab.ds")
    ds_mock.load_time_dfs.return_value = [
        trpl.read_file(filepath).aggregate_along_wavelength()
        for filepath in IMGDIR.glob("*.img")
    ]
    table = v_figure_tab.update_table(
        selected_items,
        upload_dir,
        wavelength_range,
        fitting,
        normalize_intensity,
    )
    assert table == pd.concat(ds_mock.load_time_dfs.return_value).to_dict("records")
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    ds_mock.load_time_dfs.assert_called_once_with(
        ds_mock.get_existing_item_filepaths.return_value,
        tuple(wavelength_range),
        fitting,
        normalize_intensity,
    )


@pytest.mark.parametrize("selected_items", [list(), None])
def test_update_table_when_selected_items_is_empty_or_None(
    selected_items: list[str] | None,
    upload_dir: str,
    wavelength_range: list[int],
) -> None:
    table = v_figure_tab.update_table(
        selected_items,
        upload_dir,
        wavelength_range,
        fitting=False,
        normalize_intensity=False,
    )
    assert table is None


def test_update_wavelength_slider_range_when_items_are_selected(
    selected_items: list[str],
    upload_dir: str,
    mocker: pytest_mock.MockerFixture,
) -> None:
    ds_mock = mocker.patch("dawa_trpl.components.tabs.v_figure_tab.ds")
    ds_mock.get_existing_item_filepaths.return_value = [
        os.path.join(upload_dir, item) for item in selected_items
    ]
    wavelength = np.linspace(435, 535, 640)
    ds_mock.load_trpl_data.return_value.wavelength = wavelength
    assert v_figure_tab.update_wavelength_slider_range(selected_items, upload_dir) == (
        int(wavelength.min()),
        int(wavelength.max()),
    )
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )


@pytest.mark.parametrize("selected_items", [list(), None])
def test_update_wavelength_slider_range_when_selected_items_is_empty_or_None(
    selected_items: list[str] | None,
    upload_dir: str,
) -> None:
    with pytest.raises(dash.exceptions.PreventUpdate):
        v_figure_tab.update_wavelength_slider_range(selected_items, upload_dir)


@pytest.mark.parametrize("selected_items", [list(), None])
def test_update_download_button_ability_when_no_item_is_selected(
    selected_items: list[str] | None,
) -> None:
    assert v_figure_tab.update_download_button_ability(selected_items)


def test_update_download_button_ability_when_one_item_is_selected(
    selected_items: list[str],
) -> None:
    assert not v_figure_tab.update_download_button_ability(selected_items)


@pytest.mark.parametrize(
    "selected_items", [[f"item{i}.img" for i in range(j)] for j in range(2, 5)]
)
def test_update_download_button_ability_when_multiple_items_are_selected(
    selected_items: list[str],
) -> None:
    assert v_figure_tab.update_download_button_ability(selected_items)


@pytest.mark.parametrize("fitting", [True, False])
@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_download_csv(
    selected_items: list[str],
    upload_dir: str,
    wavelength_range: list[int],
    fitting: bool,
    normalize_intensity: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    ds_mock = mocker.patch("dawa_trpl.components.tabs.v_figure_tab.ds")
    ds_mock.get_existing_item_filepaths.return_value = [
        os.path.join(upload_dir, item) for item in selected_items
    ]
    assert v_figure_tab.download_csv(
        1, selected_items, upload_dir, wavelength_range, fitting, normalize_intensity
    ) == dict(
        filename=f"v({wavelength_range[0]}-{wavelength_range[1]})-"
        + selected_items[0]
        + ".csv",
        content=ds_mock.load_time_df.return_value.to_csv.return_value,
        type="text/csv",
        base64=False,
    )
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    ds_mock.load_time_df.assert_called_once_with(
        ds_mock.get_existing_item_filepaths.return_value[0],
        tuple(wavelength_range),
        fitting,
        normalize_intensity,
    )


@pytest.mark.parametrize("selected_items", [list(), None])
def test_download_csv_when_no_item_is_selected(
    selected_items: list[str],
    upload_dir: str,
    wavelength_range: list[int],
) -> None:
    with pytest.raises(dash.exceptions.PreventUpdate):
        v_figure_tab.download_csv(
            1,
            selected_items,
            upload_dir,
            wavelength_range,
            fitting=False,
            normalize_intensity=False,
        )


def test_download_csv_when_selected_item_does_not_exist(
    selected_items: list[str],
    upload_dir: str,
    wavelength_range: list[int],
    mocker: pytest_mock.MockerFixture,
) -> None:
    mocker.patch(
        "dawa_trpl.data_system.get_existing_item_filepaths", return_value=list()
    )
    with pytest.raises(dash.exceptions.PreventUpdate):
        v_figure_tab.download_csv(
            1,
            selected_items,
            upload_dir,
            wavelength_range,
            fitting=False,
            normalize_intensity=False,
        )

import base64
import os

import dash
import plotly.graph_objects as go
import pytest
import pytest_mock

from dawa_trpl.components.tabs import streak_image_tab


@pytest.fixture()
def selected_items() -> list[str]:
    return ["item.img"]


def test_update_streak_image_when_items_are_selected(
    selected_items: list[str] | None,
    upload_dir: str,
    mocker: pytest_mock.MockerFixture,
) -> None:
    process_mock = mocker.patch("dawa_trpl.components.tabs.streak_image_tab.process")
    ds_mock = mocker.patch("dawa_trpl.components.tabs.streak_image_tab.ds")
    fig = streak_image_tab.update_streak_image(selected_items, upload_dir)
    assert fig == process_mock.create_figure.return_value
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    filepaths = ds_mock.get_existing_item_filepaths.return_value
    for call, filepath in zip(ds_mock.load_trpl_data.call_args_list, filepaths):
        assert call == mocker.call(filepath)
    process_mock.create_figure.assert_called_once_with(
        {
            os.path.basename(filepath): ds_mock.load_trpl_data.return_value
            for filepath in filepaths
        }
    )


@pytest.mark.parametrize("selected_items", [list(), None])
def test_update_streak_image_when_selected_items_is_empty_or_None(
    selected_items: list[str] | None,
    upload_dir: str,
) -> None:
    assert (
        streak_image_tab.update_streak_image(selected_items, upload_dir) == go.Figure()
    )


@pytest.mark.parametrize("selected_items", [list(), None])
def test_update_download_button_ability_when_no_item_is_selected(
    selected_items: list[str] | None,
) -> None:
    assert streak_image_tab.update_download_button_ability(selected_items)


def test_update_download_button_ability_when_one_item_is_selected(
    selected_items: list[str],
) -> None:
    assert not streak_image_tab.update_download_button_ability(selected_items)


@pytest.mark.parametrize(
    "selected_items", [[f"item{i}.img" for i in range(j)] for j in range(2, 5)]
)
def test_update_download_button_ability_when_multiple_items_are_selected(
    selected_items: list[str],
) -> None:
    assert streak_image_tab.update_download_button_ability(selected_items)


def test_download_img(
    selected_items: list[str],
    upload_dir: str,
    mocker: pytest_mock.MockerFixture,
) -> None:
    ds_mock = mocker.patch("dawa_trpl.components.tabs.streak_image_tab.ds")
    ds_mock.get_existing_item_filepaths.return_value = [
        os.path.join(upload_dir, item) for item in selected_items
    ]
    raw_binary = b"raw_binary"
    ds_mock.load_trpl_data.return_value.to_raw_binary.return_value = raw_binary
    assert streak_image_tab.download_img(2, selected_items, upload_dir) == dict(
        filename=selected_items[0],
        content=base64.urlsafe_b64encode(raw_binary).decode(),
        type="application/octet-stream",
        base64=True,
    )
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    ds_mock.load_trpl_data.assert_called_once_with(
        ds_mock.get_existing_item_filepaths.return_value[0],
    )


@pytest.mark.parametrize("selected_items", [list(), None])
def test_download_img_when_no_item_is_selected(
    selected_items: list[str],
    upload_dir: str,
) -> None:
    with pytest.raises(dash.exceptions.PreventUpdate):
        streak_image_tab.download_img(
            1,
            selected_items,
            upload_dir,
        )


def test_download_img_when_selected_item_does_not_exist(
    selected_items: list[str],
    upload_dir: str,
    mocker: pytest_mock.MockerFixture,
) -> None:
    mocker.patch(
        "dawa_trpl.data_system.get_existing_item_filepaths", return_value=list()
    )
    with pytest.raises(dash.exceptions.PreventUpdate):
        streak_image_tab.download_img(
            1,
            selected_items,
            upload_dir,
        )

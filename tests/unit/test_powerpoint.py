import os
import pathlib

import dash
import pytest
import pytest_mock
from tlab_analysis import trpl

from dawa_trpl import powerpoint
from tests import IMGDIR, FixtureRequest


@pytest.fixture(scope="module", params=[path.name for path in IMGDIR.glob("*.img")])
def trpl_data(request: FixtureRequest[str]) -> trpl.TRPLData:
    filepath = IMGDIR / request.param
    return trpl.read_file(filepath)


@pytest.mark.parametrize("selected_items", [list(), None])
def test_update_download_button_ability_when_no_item_is_selected(
    selected_items: list[str] | None,
) -> None:
    assert powerpoint.update_download_button_ability(selected_items)


@pytest.mark.parametrize("selected_items", [["item.img"]])
def test_update_download_button_ability_when_one_item_is_selected(
    selected_items: list[str],
) -> None:
    assert not powerpoint.update_download_button_ability(selected_items)


@pytest.mark.parametrize(
    "selected_items", [[f"item{i}.img" for i in range(j)] for j in range(2, 5)]
)
def test_update_download_button_ability_when_multiple_items_are_selected(
    selected_items: list[str],
) -> None:
    assert powerpoint.update_download_button_ability(selected_items)


@pytest.mark.parametrize("selected_items", [["item.img"]])
@pytest.mark.parametrize("wavelength_range", [[460, 480]])
def test_download_powerpoint_when_items_are_selected(
    selected_items: list[str],
    upload_dir: str,
    wavelength_range: list[int],
    trpl_data: trpl.TRPLData,
    mocker: pytest_mock.MockerFixture,
) -> None:
    get_existing_item_filepaths_mock = mocker.patch(
        "dawa_trpl.data_system.get_existing_item_filepaths", return_value=["item.img"]
    )
    mocker.patch("dawa_trpl.data_system.load_trpl_data", return_value=trpl_data)
    validate_upload_dir_mock = mocker.patch("dawa_trpl.data_system.validate_upload_dir")
    result = powerpoint.download_powerpoint(
        n_clicks=1,
        selected_items=selected_items,
        upload_dir=upload_dir,
        wavelength_range=wavelength_range,
        h_fig=None,
        v_fig=None,
        experiment_date=None,
    )
    assert (
        result["filename"] == pathlib.Path(selected_items[0]).with_suffix(".pptx").name
    )
    assert result["type"] == "application/octet-stream"
    assert result["base64"] is True
    # TODO: How to assert `content`?
    assert set(result.keys()) == {"filename", "content", "type", "base64"}
    validate_upload_dir_mock.assert_called_once_with(upload_dir)
    get_existing_item_filepaths_mock.assert_called_once_with(
        selected_items,
        validate_upload_dir_mock.return_value,
    )


@pytest.mark.parametrize("selected_items", [None, []])
def test_download_powerpoint_when_no_item_is_selected(
    selected_items: list[str] | None, upload_dir: str
) -> None:
    with pytest.raises(dash.exceptions.PreventUpdate):
        powerpoint.download_powerpoint(
            n_clicks=1,
            selected_items=selected_items,
            upload_dir=upload_dir,
            wavelength_range=[400, 500],
            h_fig=None,
            v_fig=None,
            experiment_date=None,
        )


@pytest.mark.parametrize("selected_items", [["unexist.img"]])
def test_download_powerpoint_when_selected_item_does_not_exist(
    selected_items: list[str], upload_dir: str
) -> None:
    assert not os.path.exists(os.path.join(upload_dir, selected_items[0]))
    with pytest.raises(dash.exceptions.PreventUpdate):
        powerpoint.download_powerpoint(
            n_clicks=1,
            selected_items=selected_items,
            upload_dir=upload_dir,
            wavelength_range=[400, 500],
            h_fig=None,
            v_fig=None,
            experiment_date=None,
        )

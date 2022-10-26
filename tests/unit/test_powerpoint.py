import os
import pathlib
from collections import abc
from unittest import mock

import dash
import pytest
import tlab_analysis.photo_luminescence as pl

from dawa_trpl import data_system as ds
from dawa_trpl import powerpoint
from tests import IMGDIR, FixtureRequest


@pytest.fixture(scope="module", params=[path.name for path in IMGDIR.glob("*.img")])
def pldata(request: FixtureRequest[str]) -> pl.Data:
    filepath = IMGDIR / request.param
    return pl.read_img(filepath)


@pytest.fixture(scope="module")
def time_resolved(pldata: pl.Data) -> pl.TimeResolved:
    return pldata.resolve_along_time()


@pytest.fixture(scope="module")
def wavelength_resolved(pldata: pl.Data) -> pl.WavelengthResolved:
    wr = pldata.resolve_along_wavelength()
    return ds._fit_to_wavelength_resolved(wr)


@pytest.fixture()
def ds_mock(
    pldata: pl.Data,
    time_resolved: pl.TimeResolved,
    wavelength_resolved: pl.WavelengthResolved,
) -> abc.Generator[mock.Mock, None, None]:
    with mock.patch("dawa_trpl.powerpoint.ds") as m:
        m.get_existing_item_filepaths.return_value = ["item.img"]
        m.load_pldata.return_value = pldata
        m.load_time_resolved.return_value = time_resolved
        m.load_wavelength_resolved.return_value = wavelength_resolved
        yield m


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
@pytest.mark.parametrize("wavelength_range", [[400, 500]])
def test_download_powerpoint_when_items_are_selected(
    ds_mock: mock.Mock,
    selected_items: list[str],
    upload_dir: str,
    wavelength_range: list[int],
) -> None:  # TODO: Refactor me
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
    ds_mock.validate_upload_dir.assert_called_once_with(upload_dir)
    ds_mock.get_existing_item_filepaths.assert_called_once_with(
        selected_items,
        ds_mock.validate_upload_dir.return_value,
    )
    ds_mock.load_time_resolved.assert_called_once_with(
        ds_mock.get_existing_item_filepaths.return_value[0]
    )
    ds_mock.load_wavelength_resolved.assert_called_once_with(
        ds_mock.get_existing_item_filepaths.return_value[0],
        tuple(wavelength_range),
        fitting=True,
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

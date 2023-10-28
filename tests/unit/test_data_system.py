import os
import pathlib

import pandas as pd
import pytest
import pytest_mock
from tlab_analysis import trpl, utils

from dawa_trpl import data_system as ds
from tests import IMGDIR, FixtureRequest


def test_validate_upload_dir_with_valid_upload_dir(
    dirname: str, upload_basedir: str
) -> None:
    upload_dir = os.path.join(upload_basedir, dirname)
    assert ds.validate_upload_dir(upload_dir) == upload_dir


def test_validate_upload_dir_when_upload_dir_is_None() -> None:
    with pytest.raises(ValueError):
        ds.validate_upload_dir(None)


def test_validate_upload_dir_when_upload_dir_is_not_under_upload_basedir(
    tmpdir: str,
) -> None:
    with pytest.raises(ValueError):
        ds.validate_upload_dir(str(tmpdir))


@pytest.mark.parametrize("item_name", [f"item{i}.img" for i in range(2)])
def test_get_item_filepath_when_filepath_exists(
    item_name: str,
    upload_dir: str,
) -> None:
    filepath = os.path.join(upload_dir, item_name)
    pathlib.Path(filepath).touch()
    assert ds.get_item_filepath(item_name, upload_dir) == filepath


@pytest.mark.parametrize("item_name", [f"item{i}.img" for i in range(2)])
def test_get_item_filepath_when_filepath_does_not_exist(
    item_name: str,
    upload_dir: str,
) -> None:
    assert ds.get_item_filepath(item_name, upload_dir) is None


@pytest.mark.parametrize("item_names", [["item.img"]])
def test_get_item_filepaths(
    item_names: list[str],
    upload_dir: str,
) -> None:
    filepaths = [
        ds.get_item_filepath(
            item_name,
            upload_dir,
        )
        for item_name in item_names
    ]
    assert (
        ds.get_item_filepaths(
            item_names,
            upload_dir,
        )
        == filepaths
    )


@pytest.mark.parametrize("item_names", [["exist.img", "unexist.img"]])
def test_existing_item_filepaths(
    item_names: list[str],
    upload_dir: str,
) -> None:
    exist_path = os.path.join(upload_dir, item_names[0])
    pathlib.Path(exist_path).touch()
    assert ds.get_existing_item_filepaths(item_names, upload_dir) == [exist_path]


@pytest.fixture(params=[path.name for path in IMGDIR.glob("*.img")])
def filepath(request: FixtureRequest[str]) -> str:
    return os.path.join(IMGDIR, request.param)


def test_load_trpl_data(filepath: str) -> None:
    assert ds.load_trpl_data(filepath) == trpl.read_file(filepath)  # type: ignore[arg-type]


def test_load_wavelength_df(filepath: str) -> None:
    actual = ds.load_wavelength_df(filepath)
    expected = ds.load_trpl_data(filepath).aggregate_along_time()
    expected["smoothed_intensity"] = utils.smooth(expected["intensity"].to_list())
    pd.testing.assert_series_equal(actual["wavelength"], expected["wavelength"])
    pd.testing.assert_series_equal(actual["intensity"], expected["intensity"])
    pd.testing.assert_series_equal(
        actual["smoothed_intensity"], expected["smoothed_intensity"]
    )
    assert all(actual["name"] == os.path.basename(filepath))


@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_load_wavelength_df_with_normalize_intensity(
    filepath: str, normalize_intensity: bool
) -> None:
    wdf = ds.load_wavelength_df(filepath, normalize_intensity)
    assert bool(wdf["intensity"].max() == 1.0) is normalize_intensity


@pytest.fixture(params=["single_filepath", "multiple_filepaths"])
def filepaths(request: FixtureRequest[str]) -> list[str]:
    filepaths = [str(path) for path in IMGDIR.glob("*.img")]
    match request.param:
        case "single_filepath":
            return filepaths[:1]
        case "multiple_filepaths":
            return filepaths
        case _:
            raise NotImplementedError


@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_load_wavelength_dfs(
    filepaths: list[str],
    normalize_intensity: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    load_wavelength_df_mock = mocker.patch("dawa_trpl.data_system.load_wavelength_df")
    wdfs = [mocker.Mock() for _ in filepaths]
    load_wavelength_df_mock.side_effect = wdfs
    assert ds.load_wavelength_dfs(filepaths, normalize_intensity) == wdfs
    for call, filepath in zip(
        load_wavelength_df_mock.call_args_list, filepaths, strict=True
    ):
        assert call == mocker.call(filepath, normalize_intensity=normalize_intensity)


@pytest.mark.parametrize("wavelength_range", [(440, 470), (460, 500)])
def test_load_time_df(
    filepath: str,
    wavelength_range: tuple[float, float],
) -> None:
    actual = ds.load_time_df(filepath, wavelength_range)
    expected = ds.load_trpl_data(filepath).aggregate_along_wavelength(wavelength_range)
    expected["smoothed_intensity"] = utils.smooth(expected["intensity"].to_list())
    pd.testing.assert_series_equal(actual["time"], expected["time"])
    pd.testing.assert_series_equal(actual["intensity"], expected["intensity"])
    pd.testing.assert_series_equal(
        actual["smoothed_intensity"], expected["smoothed_intensity"]
    )
    assert all(actual["name"] == os.path.basename(filepath))
    # TODO: Assert wr.df["fit"] is filled with nan


@pytest.fixture()
def wavelength_range() -> tuple[float, float]:
    return (450, 500)


@pytest.mark.parametrize("fitting", [True, False])
def test_load_time_df_with_fitting(
    filepath: str,
    wavelength_range: tuple[float, float],
    fitting: bool,
) -> None:
    tdf = ds.load_time_df(filepath, wavelength_range, fitting=fitting)
    assert bool(tdf.attrs.get("fit") is not None) is fitting
    if fitting:
        assert set(tdf.attrs["fit"].keys()) == {
            "a",
            "tau1",
            "b",
            "tau2",
            "params",
            "cov",
        }
    # TODO: Assert wr.df["fit"] is valid


@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_load_time_df_with_normalize_intensity(
    filepath: str,
    wavelength_range: tuple[float, float],
    normalize_intensity: bool,
) -> None:
    tdf = ds.load_time_df(
        filepath, wavelength_range, normalize_intensity=normalize_intensity
    )
    assert bool(tdf["intensity"].max() == 1.0) is normalize_intensity


@pytest.mark.parametrize("fitting", [True, False])
@pytest.mark.parametrize("normalize_intensity", [True, False])
def test_load_time_dfs(
    filepaths: list[str],
    wavelength_range: tuple[float, float],
    fitting: bool,
    normalize_intensity: bool,
    mocker: pytest_mock.MockerFixture,
) -> None:
    tdfs = [mocker.Mock() for _ in filepaths]
    load_time_df_mock = mocker.patch("dawa_trpl.data_system.load_time_df")
    load_time_df_mock.side_effect = tdfs
    assert (
        ds.load_time_dfs(
            filepaths,
            wavelength_range,
            fitting,
            normalize_intensity,
        )
        == tdfs
    )
    for call, filepath in zip(load_time_df_mock.call_args_list, filepaths, strict=True):
        assert call == mocker.call(
            filepath,
            wavelength_range=wavelength_range,
            fitting=fitting,
            normalize_intensity=normalize_intensity,
        )

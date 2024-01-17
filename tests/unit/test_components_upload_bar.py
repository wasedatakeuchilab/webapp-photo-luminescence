import base64
import filecmp
import os
import pathlib

import dash
import pytest
from dawa_trpl.components import upload_bar

from tests import IMGDIR, FixtureRequest


def test_update_upload_dir_when_upload_dir_already_exists(
    dirname: str, upload_basedir: str
) -> None:
    upload_dir = os.path.join(upload_basedir, dirname)
    with pytest.raises(dash.exceptions.PreventUpdate):
        upload_bar.update_upload_dir(upload_dir)


@pytest.mark.parametrize("upload_dir", ["", None])
def test_update_upload_dir_when_upload_dir_does_not_exist_yet(
    upload_dir: str, upload_basedir: str
) -> None:
    assert upload_bar.update_upload_dir(upload_dir).startswith(upload_basedir)


@pytest.fixture()
def filenames(datapaths: list[str]) -> list[str]:
    return [os.path.basename(path) for path in datapaths]


@pytest.fixture()
def contents(datapaths: list[str]) -> list[str]:
    def read_binary(datapath: str) -> bytes:
        with open(datapath, "rb") as f:
            return f.read()

    def raw_to_content(raw: bytes) -> str:
        content_type = "application/octet-stream"
        return content_type + "," + base64.urlsafe_b64encode(raw).decode()

    raws = map(read_binary, datapaths)
    contents = map(raw_to_content, raws)
    return list(contents)


@pytest.fixture(params=["single_file", "multiple_files"])
def datapaths(request: FixtureRequest[str]) -> list[str]:
    datapaths = [str(path) for path in IMGDIR.glob("*.img")]
    match request.param:
        case "single_file":
            return datapaths[:1]
        case "multiple_files":
            return datapaths
        case _:
            raise NotImplementedError


def test_on_upload_files_when_files_are_uploaded(
    datapaths: list[str],
    contents: list[str],
    filenames: list[str],
    upload_dir: str,
) -> None:
    assert len(filenames) == len(contents)
    assert upload_bar.on_upload_files(contents, filenames, upload_dir) == filenames
    for datapath in datapaths:
        uploaded_path = os.path.join(upload_dir, os.path.basename(datapath))
        assert os.path.exists(uploaded_path)
        assert filecmp.cmp(uploaded_path, datapath)


def test_on_upload_files_when_contents_is_None(upload_dir: str) -> None:
    contents = None
    filenames = ["dummy.img"]
    with pytest.raises(dash.exceptions.PreventUpdate):
        upload_bar.on_upload_files(contents, filenames, upload_dir)


def test_on_upload_files_when_filenames_is_None(upload_dir: str) -> None:
    contents = ["application/octet-stream,content_string"]
    filenames = None
    with pytest.raises(dash.exceptions.PreventUpdate):
        upload_bar.on_upload_files(contents, filenames, upload_dir)


@pytest.fixture(params=["empty", "only_file", "include_dir"])
def dropdown_options(request: FixtureRequest[str], upload_dir: str) -> list[str]:
    upload_dirpath = pathlib.Path(upload_dir)
    match request.param:
        case "only_file" | "include_dir":
            (upload_dirpath / "uploaded_file.img").touch()
        case "include_dir":
            (upload_dirpath / "subdir").mkdir()
    return [path.name for path in upload_dirpath.iterdir() if path.is_file()]


def test_update_dropdown_options(dropdown_options: list[str], upload_dir: str) -> None:
    assert upload_bar.update_dropdown_options(None, upload_dir) == dropdown_options


@pytest.mark.parametrize(
    "filenames", [["filename"], [], None], ids=["has_value", "empty", "none"]
)
@pytest.mark.parametrize(
    "current_value", [["dropdown_option"], [], None], ids=["has_value", "empty", "none"]
)
def test_update_dropdown_value(
    filenames: list[str] | None, current_value: list[str] | None
) -> None:
    dropdown_value = upload_bar.update_dropdown_value(filenames, current_value)
    filenames = filenames if filenames is not None else list()
    current_value = current_value if current_value is not None else list()
    assert dropdown_value == current_value + filenames

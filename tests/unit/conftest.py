import tempfile
from collections import abc

import pytest
import pytest_mock

from tests import FixtureRequest


@pytest.fixture(autouse=True)
def upload_basedir(mocker: pytest_mock.MockerFixture) -> abc.Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        mocker.patch("dawa_trpl.config.UPLOAD_BASEDIR", new=tmpdir)
        yield tmpdir


@pytest.fixture()
def upload_dir(upload_basedir: str) -> abc.Generator[str, None, None]:
    with tempfile.TemporaryDirectory(dir=upload_basedir) as tmpdir:
        yield tmpdir


@pytest.fixture(params=[f"dirname{i}" for i in range(3)])
def dirname(request: FixtureRequest[str]) -> str:
    return request.param

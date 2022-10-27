import tempfile
from collections import abc
from unittest import mock

import pytest

from tests import FixtureRequest


@pytest.fixture(scope="module", autouse=True)
def upload_basedir() -> abc.Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        with mock.patch("dawa_trpl.config.UPLOAD_BASEDIR", tmpdir):
            yield tmpdir


@pytest.fixture()
def upload_dir(upload_basedir: str) -> abc.Generator[str, None, None]:
    with tempfile.TemporaryDirectory(dir=upload_basedir) as tmpdir:
        yield tmpdir


@pytest.fixture(params=[f"dirname{i}" for i in range(3)])
def dirname(request: FixtureRequest[str]) -> str:
    return request.param

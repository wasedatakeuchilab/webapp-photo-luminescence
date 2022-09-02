import pathlib
import typing as t

import pytest

PT = t.TypeVar("PT")

TESTDATADIR = pathlib.Path(__file__).parent / "testdata"
IMGDIR = TESTDATADIR / "img"


class FixtureRequest(pytest.FixtureRequest, t.Generic[PT]):
    param: PT

import os
import tempfile

_PREFIX = "DAWA_TRPL_"
URL_BASE_PATH = os.environ.get(_PREFIX + "URL_BASE_PATH", "/")
UPLOAD_BASEDIR = os.environ.get(
    _PREFIX + "UPLOAD_BASEDIR", tempfile.mkdtemp(prefix="dawa_trpl_")
)

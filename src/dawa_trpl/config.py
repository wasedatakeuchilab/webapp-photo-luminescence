import os
import tempfile

URL_BASE_PATH = os.environ.get("URL_BASE_PATH", "/")
UPLOAD_BASEDIR = os.environ.get("UPLOAD_BASEDIR", tempfile.mkdtemp(prefix="wpl"))

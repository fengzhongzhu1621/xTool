import os

from xTool.contextmanagers.temp import temp_path


def test_temp_path():
    with temp_path("file") as path:
        basename = os.path.basename(path)
        assert basename == "file"

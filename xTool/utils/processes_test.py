import os

from xTool.utils import processes


def test_which():
    values = processes.which("Lib", path=None)
    for executable_path in values:
        assert os.access(executable_path, os.X_OK)

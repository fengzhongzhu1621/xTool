# -*- coding: utf-8 -*-

from xTool.config.file_loader import FileConfigLoader


class TestFileConfigLoader:
    def test_load(self):
        file_path = "./data.txt"
        loader = FileConfigLoader()
        actual = loader.load(file_path)
        assert loader.file_path == file_path
        assert actual == b'hello world!'

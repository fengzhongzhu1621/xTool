# -*- coding: utf-8 -*-

import os
from unittest import TestCase
import pytest
from xTool.utils.file import write_temp_file
from xTool.plugins import data_source_provider
from xTool.plugins.plugin import (
    PluginType,
    get_plugin_instance)
from xTool.plugins.exceptions import PluginDataSourceException


class TestFileDataProvider(TestCase):
    def test_load(self):
        plugin_instance = get_plugin_instance(PluginType.CONFIG_DATA_SOURCE, "FileDataProvider")
        file_content = b"file content"
        file_path = write_temp_file(file_content, delete=False)
        actual = plugin_instance.load(file_path)
        assert actual == file_content

        options = {
            "file_path": file_path
        }
        actual = plugin_instance.load(file_path=None, options=options)
        assert actual == file_content

        with pytest.raises(PluginDataSourceException):
            plugin_instance.load(file_path=None, options={})
        os.unlink(file_path)

    def test_set_options(self):
        plugin_instance = get_plugin_instance(PluginType.CONFIG_DATA_SOURCE, "FileDataProvider")
        options = {
            "file_path": "file_path"
        }
        plugin_instance.set_options(options)
        assert plugin_instance.options == options

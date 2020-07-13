# -*- coding: utf-8 -*-

from unittest import TestCase
from xTool.plugins.plugin import (
    PluginType,
    get_plugin_instance)
from xTool.plugins import json_decoder


class TestJsonDecoder(TestCase):
    def test_load(self):
        plugin_instance = get_plugin_instance(
            PluginType.CONFIG_DECODER, "JSONDecoder")
        config_data = '{"a": 1, "b": 2}'
        actual = plugin_instance.decode(config_data)
        assert actual == {"a": 1, "b": 2}

# -*- coding: utf-8 -*-
import yaml
from xTool.plugins.decoder import IBaseDecoder
from xTool.plugins.plugin import PluginType, PluginComponent
from xTool.misc import tou


class YamlDecoder(IBaseDecoder, PluginComponent):
    plugin_type = PluginType.CONFIG_DECODER

    def __init__(self):
        super().__init__()
        self.options = None

    def decode(self, config_data: bytes, options: dict = None) -> dict:
        config = yaml.load(tou(config_data, Loader=yaml.FullLoader))
        return config

    def set_options(self, options: dict) -> None:
        self.options=options

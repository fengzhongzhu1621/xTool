# -*- coding: utf-8 -*-

from xTool.plugins.plugin import register_plugin, PluginType
from .base import ConfigLoaderType


@register_plugin(
    PluginType.COMPRESS, ConfigLoaderType.FILE
)
class FileConfigLoader:
    def __init__(self):
        self.file_path = None

    def load(self, file_path: str = None) -> bytes:
        if file_path:
            self.file_path = file_path
        with open(self.file_path, 'rb') as reader:
            return reader.read()

    def set_file_path(self, file_path):
        self.file_path = file_path

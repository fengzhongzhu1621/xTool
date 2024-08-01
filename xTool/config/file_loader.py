from xTool.plugin import PluginType, register_plugin

from .base import ConfigLoaderType


@register_plugin(PluginType.ConfigLoader, ConfigLoaderType.FILE)
class FileConfigLoader:
    def __init__(self):
        self.file_path = None

    def load(self, file_path: str = None) -> bytes:
        if file_path:
            self.file_path = file_path
        with open(self.file_path, "rb") as reader:
            return reader.read()

    def set_file_path(self, file_path):
        self.file_path = file_path

from typing import Dict


class PluginStore:
    __slots__ = ("plugins", "plugin_instances")

    def __init__(self):
        self.plugins = {}  # 存放所有的插件
        self.plugin_instances = {}  # 存放所有的插件实例化对象，一个插件只有一个实例化对象

    def add_plugin(self, plugin_type, plugin_name, plugin_class) -> None:
        """注册插件类 ."""
        self.plugins.setdefault(plugin_type, {})[plugin_name] = plugin_class

    def get_plugin(self, plugin_type, plugin_name):
        """获得已注册的插件类 ."""
        return self.plugins.get(plugin_type, {}).get(plugin_name)

    def add_plugin_instance(self, plugin_type, plugin_name, plugin_instance):
        """注册插件实例 ."""
        self.plugin_instances.setdefault(plugin_type, {})[plugin_name] = plugin_instance

    def get_plugin_instance(self, plugin_type, plugin_name):
        """获得插件实例 ."""
        return self.plugin_instances.get(plugin_type, {}).get(plugin_name)

    def get_all_plugin(self) -> Dict:
        return self.plugins

    def destroy_plugins(self) -> None:
        self.plugins = {}
        self.plugin_instances = {}


DefaultPluginStore = PluginStore()

from xTool.plugin import DefaultPluginStore


class PluginFancyDict(dict):
    def __getattr__(self, plugin_name):
        try:
            plugin = self[plugin_name]
            return plugin.create_instance()
        except KeyError as k:
            raise AttributeError(k)


class ResourceInstance:
    def __getattr__(self, plugin_type):
        if plugin_type.startswith("_"):
            return None
        # 获取资源插件实例
        result = DefaultPluginStore.plugins.get(plugin_type, {})
        return PluginFancyDict(result)


api = ResourceInstance()

from xTool.plugin import (
    PluginType,
    get_plugin_instance)


class ResourceInstance:
    def __getattr__(self, resource_name):
        if resource_name.startswith("_"):
            return None
        return get_plugin_instance(PluginType.drf_resource, resource_name)


api = ResourceInstance()

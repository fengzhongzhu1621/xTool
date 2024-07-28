"""
注册插件有两种方式

1. 添加装饰器 @register_plugin
2. 从 PluginRegister 类继承

"""

from xTool.plugin import PluginRegister, PluginType, get_plugin_instance, register_plugin


@register_plugin(PluginType.UNITTEST, "unittest")
class Plugin:
    a = 1

    def __init__(self):
        self.b = 2


class Plugin2(PluginRegister):
    plugin_type = PluginType.UNITTEST
    plugin_name = "unittest2"

    a = 1

    def __init__(self):
        self.b = 2


def test_register_plugin():
    plugin_instance = get_plugin_instance(PluginType.UNITTEST, "unittest")
    assert plugin_instance.a == 1
    assert plugin_instance.b == 2

    plugin_instance = get_plugin_instance(PluginType.UNITTEST, "unittest2")
    assert plugin_instance.a == 1
    assert plugin_instance.b == 2

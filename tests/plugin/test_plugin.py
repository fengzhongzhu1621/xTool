# -*- coding: utf-8 -*-

from xTool.plugin import (
    PluginType,
    register_plugin,
    get_plugin_instance,
    PluginRegister
)


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

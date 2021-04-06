# -*- coding: utf-8 -*-

from xTool.patterns.filter.chain import FilterChain
from xTool.plugins.plugin import get_plugin_instance
from xTool.plugins.plugin import PluginType
from tests.patterns.filter import BusinessMethod, BusinessAfterFilter, BusinessBeforeFilter


class Context:
    def __init__(self):
        self.value = []


def test_filter_plugin():
    filter_chain = FilterChain(BusinessMethod())
    before_filter = get_plugin_instance(PluginType.BEFORE_FILTER, "test")
    assert isinstance(before_filter, BusinessBeforeFilter)
    after_filter = get_plugin_instance(PluginType.AFTER_FILTER, "test")
    assert isinstance(after_filter, BusinessAfterFilter)
    filter_chain.add_filter(before_filter)
    filter_chain.add_filter(after_filter)
    context = Context()
    result = filter_chain.process(context)
    assert result.value == [1, 2, 3]


async def test_filter_plugin_awaitable_process(loop):
    filter_chain = FilterChain(BusinessMethod())
    before_filter = get_plugin_instance(PluginType.BEFORE_FILTER, "test")
    assert isinstance(before_filter, BusinessBeforeFilter)
    after_filter = get_plugin_instance(PluginType.AFTER_FILTER, "test")
    assert isinstance(after_filter, BusinessAfterFilter)
    filter_chain.add_filter(before_filter)
    filter_chain.add_filter(after_filter)
    context = Context()
    result = await filter_chain.async_process(context)
    assert result.value == [11, 22, 33]

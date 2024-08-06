from xTool.design_patterns.filter.chain import FilterChain
from xTool.plugin import PluginType, get_plugin_instance
from xTool.testing.test_filter import BusinessAfterFilter, BusinessBeforeFilter, BusinessMethod, Context


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


async def test_filter_plugin_awaitable_process(event_loop):
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

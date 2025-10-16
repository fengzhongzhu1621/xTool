from xTool.design_patterns.filter.chain import FilterChain
from xTool.testing.test_filter import BusinessAfterFilter, BusinessBeforeFilter, BusinessMethod, Context


def test_filter_chain_process():
    filter_chain = FilterChain(BusinessMethod())

    filter_chain.add_filter(BusinessBeforeFilter())
    filter_chain.add_filter(BusinessAfterFilter())

    context = Context()
    result = filter_chain.process(context)
    assert result.value == [1, 2, 3]


async def test_filter_chain_awaitable_process(event_loop):
    filter_chain = FilterChain(BusinessMethod())

    filter_chain.add_filter(BusinessBeforeFilter())
    filter_chain.add_filter(BusinessAfterFilter())

    context = Context()
    result = await filter_chain.async_process(context)
    assert result.value == [11, 22, 33]

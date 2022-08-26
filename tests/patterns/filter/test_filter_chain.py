# -*- coding: utf-8 -*-

from xTool.patterns.filter.chain import FilterChain
from . import BusinessMethod, BusinessAfterFilter, BusinessBeforeFilter


class Context:
    def __init__(self):
        self.value = []


def test_filter_chain_process():
    filter_chain = FilterChain(BusinessMethod())
    filter_chain.add_filter(BusinessBeforeFilter())
    filter_chain.add_filter(BusinessAfterFilter())
    context = Context()
    result = filter_chain.process(context)
    assert result.value == [1, 2, 3]


async def test_filter_chain_awaitable_process(loop):
    filter_chain = FilterChain(BusinessMethod())
    filter_chain.add_filter(BusinessBeforeFilter())
    filter_chain.add_filter(BusinessAfterFilter())
    context = Context()
    result = await filter_chain.async_process(context)
    assert result.value == [11, 22, 33]

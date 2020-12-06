# -*- coding: utf-8 -*-

from xTool.algorithms.filter.chain import BeforeFilter, AfterFilter, Method, FilterChain


class Context:
    def __init__(self):
        self.value = []


class BusinessBeforeFilter(BeforeFilter):
    def before_process(self, context):
        context.value.append(1)

    async def async_before_process(self, context):
        context.value.append(11)


class BusinessAfterFilter(AfterFilter):
    def after_process(self, context):
        context.value.append(3)

    async def async_after_process(self, context):
        context.value.append(33)


class BusinessMethod(Method):
    def process_direct(self, context):
        context.value.append(2)
        return context

    async def async_process_direct(self, context):
        context.value.append(22)
        return context


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

# -*- coding: utf-8 -*-
from unittest import TestCase
from xTool.algorithms.filter.chain import BeforeFilter, AfterFilter, Method, FilterChain


class Context:
    def __init__(self):
        self.value = []


class BusinessBeforeFilter(BeforeFilter):
    def before_process(self, context):
        context.value.append(1)


class BusinessAfterFilter(AfterFilter):
    def after_process(self, context):
        context.value.append(3)


class BusinessMethod(Method):
    def process_direct(self, context):
        context.value.append(2)
        return context


class TestFilterChain(TestCase):
    def test_process(self):
        self.filter_chain = FilterChain(BusinessMethod())
        self.filter_chain.add_filter(BusinessBeforeFilter())
        self.filter_chain.add_filter(BusinessAfterFilter())
        context = Context()
        result = self.filter_chain.process(context)
        assert result.value == [1, 2, 3]

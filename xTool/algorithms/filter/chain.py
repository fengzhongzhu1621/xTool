# -*- coding: utf-8 -*-

"""
责任链模式
"""

from abc import ABCMeta, abstractmethod


class Method(metaclass=ABCMeta):
    @abstractmethod
    def process_direct(self, *args, **kwargs):
        raise NotImplementedError

    def process(self, *args, **kwargs):
        return self.process_direct(*args, **kwargs)


class IFilter(metaclass=ABCMeta):
    @abstractmethod
    def process(self, chain, method: Method, *args, **kwargs):
        raise NotImplementedError


class BeforeFilter(IFilter):
    def process(self, chain, method: Method, *args, **kwargs):
        self.before_process(*args, **kwargs)
        result = chain.process(*args, **kwargs)
        return result

    @abstractmethod
    def before_process(self, *args, **kwargs):
        raise NotImplementedError


class AfterFilter(IFilter):
    def process(self, chain, method: Method, *args, **kwargs):
        result = chain.process(*args, **kwargs)
        self.after_process(*args, **kwargs)
        return result

    @abstractmethod
    def after_process(self, *args, **kwargs):
        raise NotImplementedError


class IFilterChain(metaclass=ABCMeta):
    @abstractmethod
    def next_filter(self):
        raise NotImplementedError


class FilterChain(IFilterChain):
    def __init__(self, method: Method):
        self.method: Method = method
        self.filters: list = []
        self.index: int = 0

    def add_filter(self, filter_obj: IFilter):
        if filter_obj:
            self.filters.append(filter_obj)

    def next_filter(self):
        filter_obj = self.filters[self.index]
        self.index += 1
        return filter_obj

    def process(self, *args, **kwargs):
        if self.index < len(self.filters):
            result = self.next_filter().process(self, self.method, *args, **kwargs)
        else:
            result = self.method.process(*args, **kwargs)
        return result

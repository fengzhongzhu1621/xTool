"""
责任链模式
"""

from abc import ABCMeta, abstractmethod


class Method:
    """业务逻辑类 ."""

    def process_direct(self, *args, **kwargs):
        raise NotImplementedError

    def process(self, *args, **kwargs):
        """业务逻辑执行入口 ."""
        return self.process_direct(*args, **kwargs)

    async def async_process_direct(self, *args, **kwargs):
        raise NotImplementedError

    async def async_process(self, *args, **kwargs):
        return await self.async_process_direct(*args, **kwargs)


class IFilter:
    def process(self, chain, method: Method, *args, **kwargs):
        raise NotImplementedError

    async def async_process(self, chain, method: Method, *args, **kwargs):
        raise NotImplementedError


class BeforeFilter(IFilter):
    """前置过滤器 ."""

    def process(self, chain, method: Method, *args, **kwargs):
        self.before_process(*args, **kwargs)
        result = chain.process(*args, **kwargs)
        return result

    async def async_process(self, chain, method: Method, *args, **kwargs):
        await self.async_before_process(*args, **kwargs)
        result = await chain.async_process(*args, **kwargs)
        return result

    def before_process(self, *args, **kwargs):
        raise NotImplementedError

    async def async_before_process(self, *args, **kwargs):
        raise NotImplementedError


class AfterFilter(IFilter):
    """后置过滤器 ."""

    def process(self, chain, method: Method, *args, **kwargs):
        result = chain.process(*args, **kwargs)
        self.after_process(*args, **kwargs)
        return result

    async def async_process(self, chain, method: Method, *args, **kwargs):
        result = await chain.async_process(*args, **kwargs)
        await self.async_after_process(*args, **kwargs)
        return result

    def after_process(self, *args, **kwargs):
        raise NotImplementedError

    async def async_after_process(self, *args, **kwargs):
        raise NotImplementedError


class IFilterChain(metaclass=ABCMeta):
    @abstractmethod
    def next_filter(self):
        raise NotImplementedError


class FilterChain(IFilterChain):
    """过滤器链 ."""

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

    async def async_process(self, *args, **kwargs):
        if self.index < len(self.filters):
            result = await self.next_filter().async_process(self, self.method, *args, **kwargs)
        else:
            result = await self.method.async_process(*args, **kwargs)
        return result

# -*- coding: utf-8 -*-
"""
DNS缓存，来自aiohttp
"""

from itertools import cycle, islice
from time import monotonic
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
)


class DNSCacheTable:

    def __init__(self, ttl: Optional[float] = None) -> None:
        # 存放主机地址
        self._addrs_rr = {}  # type: Dict[Tuple[str, int], Tuple[Iterator[Dict[str, Any]], int]]  # noqa
        # 记录地址添加的单调时间
        self._timestamps = {}  # type: Dict[Tuple[str, int], float]
        # 过期时间，为None则永不过期，单位是s，可以是浮点数
        self._ttl = ttl

    def __contains__(self, host: object) -> bool:
        """in和not in调用了str对象的一个方法__contains__() ."""
        return host in self._addrs_rr

    def add(self, key: Tuple[str, int], addrs: List[Dict[str, Any]]) -> None:
        self._addrs_rr[key] = (cycle(addrs), len(addrs))

        # 记录添加的时间
        if self._ttl:
            # 单调时钟模块monotonic()用于估算长时间运行的程序的运行时间，因为即使系统时间发生了变化，它也保证不会后退。
            self._timestamps[key] = monotonic()

    def remove(self, key: Tuple[str, int]) -> None:
        self._addrs_rr.pop(key, None)

        if self._ttl:
            self._timestamps.pop(key, None)

    def clear(self) -> None:
        self._addrs_rr.clear()
        self._timestamps.clear()

    def next_addrs(self, key: Tuple[str, int]) -> List[Dict[str, Any]]:
        loop, length = self._addrs_rr[key]
        # 获得第一个切片
        addrs = list(islice(loop, length))
        # Consume one more element to shift internal state of `cycle`
        # 右移一位
        # 1 2 3 1 2 3 1 2 3 -> 2 3 1 2 3 1 2 3
        next(loop)
        return addrs

    def expired(self, key: Tuple[str, int]) -> bool:
        if self._ttl is None:
            # 永不过期
            return False

        return self._timestamps[key] + self._ttl < monotonic()


def clear_dns_cache(cached_hosts: DNSCacheTable,
                    host: Optional[str] = None,
                    port: Optional[int] = None) -> None:
    """Remove specified host/port or clear all dns local cache."""
    if host is not None and port is not None:
        cached_hosts.remove((host, port))
    elif host is not None or port is not None:
        raise ValueError("either both host and port "
                         "or none of them are allowed")
    else:
        cached_hosts.clear()

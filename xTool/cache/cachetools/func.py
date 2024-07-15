import collections
import functools
import math
import random
import time
from threading import RLock

from .fifo import FIFOCache
from .keys import hash_key, typed_key
from .lfu import LFUCache
from .lru import LRUCache
from .mru import MRUCache
from .rr import RRCache
from .ttl import TTLCache

_CacheInfo = collections.namedtuple("CacheInfo", ["hits", "misses", "maxsize", "curr_size"])


class _UnboundCache(dict):
    @property
    def maxsize(self):
        return None

    @property
    def curr_size(self):
        return len(self)


class _UnboundTTLCache(TTLCache):
    def __init__(self, ttl, timer):
        TTLCache.__init__(self, math.inf, ttl, timer)

    @property
    def maxsize(self):
        return None


def _cache(cache, typed):
    maxsize = cache.maxsize

    def decorator(func):
        key = typed_key if typed else hash_key
        hits = misses = 0
        lock = RLock()

        def wrapper(*args, **kwargs):
            nonlocal hits, misses
            k = key(*args, **kwargs)
            with lock:
                try:
                    v = cache[k]
                    # 缓存命中次数
                    hits += 1
                    return v
                except KeyError:
                    # 缓存失效次数
                    misses += 1
            v = func(*args, **kwargs)
            # in case of a race, prefer the item already in the cache
            try:
                with lock:
                    return cache.setdefault(k, v)
            except ValueError:
                return v  # value too large

        def cache_info():
            with lock:
                maxsize = cache.maxsize
                curr_size = cache.curr_size
            return _CacheInfo(hits, misses, maxsize, curr_size)

        def cache_clear():
            nonlocal hits, misses
            with lock:
                try:
                    cache.clear()
                finally:
                    hits = misses = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        wrapper.cache_parameters = lambda: {"maxsize": maxsize, "typed": typed}
        functools.update_wrapper(wrapper, func)
        return wrapper

    return decorator


def fifo_cache(maxsize=128, typed=False):
    """Decorator to wrap a function with a memoizing callable that saves
    up to `maxsize` results based on a First In First Out (FIFO)
    algorithm.

    """
    if maxsize is None:
        # 缓冲不会过期，使用dict实现
        return _cache(_UnboundCache(), typed)
    elif callable(maxsize):
        return _cache(FIFOCache(128), typed)(maxsize)
    else:
        return _cache(FIFOCache(maxsize), typed)


def lfu_cache(maxsize=128, typed=False):
    """Decorator to wrap a function with a memoizing callable that saves
    up to `maxsize` results based on a Least Frequently Used (LFU)
    algorithm.

    """
    if maxsize is None:
        return _cache(_UnboundCache(), typed)
    elif callable(maxsize):
        return _cache(LFUCache(128), typed)(maxsize)
    else:
        return _cache(LFUCache(maxsize), typed)


def lru_cache(maxsize=128, typed=False):
    """Decorator to wrap a function with a memoizing callable that saves
    up to `maxsize` results based on a Least Recently Used (LRU)
    algorithm.

    """
    if maxsize is None:
        return _cache(_UnboundCache(), typed)
    elif callable(maxsize):
        return _cache(LRUCache(128), typed)(maxsize)
    else:
        return _cache(LRUCache(maxsize), typed)


def mru_cache(maxsize=128, typed=False):
    """Decorator to wrap a function with a memoizing callable that saves
    up to `maxsize` results based on a Most Recently Used (MRU)
    algorithm.
    """
    if maxsize is None:
        return _cache(_UnboundCache(), typed)
    elif callable(maxsize):
        return _cache(MRUCache(128), typed)(maxsize)
    else:
        return _cache(MRUCache(maxsize), typed)


def rr_cache(maxsize=128, choice=random.choice, typed=False):
    """Decorator to wrap a function with a memoizing callable that saves
    up to `maxsize` results based on a Random Replacement (RR)
    algorithm.

    """
    if maxsize is None:
        return _cache(_UnboundCache(), typed)
    elif callable(maxsize):
        return _cache(RRCache(128, choice), typed)(maxsize)
    else:
        return _cache(RRCache(maxsize, choice), typed)


def ttl_cache(maxsize=128, ttl=600, timer=time.monotonic, typed=False):
    """Decorator to wrap a function with a memoizing callable that saves
    up to `maxsize` results based on a Least Recently Used (LRU)
    algorithm with a per-item time-to-live (TTL) value.
    """
    if maxsize is None:
        return _cache(_UnboundTTLCache(ttl, timer), typed)
    elif callable(maxsize):
        return _cache(TTLCache(128, ttl, timer), typed)(maxsize)
    else:
        return _cache(TTLCache(maxsize, ttl, timer), typed)

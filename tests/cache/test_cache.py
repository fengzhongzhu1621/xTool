# -*- coding: utf-8 -*-

from xTool.cache import Cache
from xTool.cache.constants import CacheInstanceType


class TestCache:
    def test_instance(self):
        cache = Cache("dummy", CacheInstanceType.InstanceCache)
        cache.set("a", 1, seconds=10)
        assert cache.get("a") == 1

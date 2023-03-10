# -*- coding: utf-8 -*-

import fakeredis

from xTool.cache import Cache
from xTool.cache.constants import CacheInstanceType, CacheBackendType


class TestCache:
    def test_instance(self):
        cache = Cache("dummy", CacheInstanceType.InstanceCache)
        cache.set("a", 1, seconds=10)
        assert cache.get("a") == 1

    def test_redis(self):
        connection_conf = {
            "host": "localhost",
            "port": "6379",
            "db": 0,
            "password": "",
        }
        cache = Cache(
            CacheBackendType.CELERY,
            CacheInstanceType.RedisCache,
            redis_class=fakeredis.FakeStrictRedis,
            connection_conf=connection_conf,
        )
        cache.set("foo", "bar")
        assert cache.get("foo") == "bar"

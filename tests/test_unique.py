# -*- coding: utf-8 -*-

import fakeredis

from xTool.cache import Cache
from xTool.cache.constants import CacheInstanceType, CacheBackendType
from xTool.unique import SequenceManager


class TestSequenceManager:

    def test_generate(self):
        connection_conf = {
            "host": "localhost",
            "port": "6379",
            "db": 0,
            "password": "",
        }
        cache = Cache(CacheBackendType.CELERY, CacheInstanceType.RedisCache, redis_class=fakeredis.FakeStrictRedis,
                      connection_conf=connection_conf)
        manager = SequenceManager(cache)
        assert manager.generate() == 1
        assert manager.generate() == 2
        assert manager.generate() == 3
        assert manager.generate() == 4

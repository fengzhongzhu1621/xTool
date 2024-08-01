import fakeredis

from xTool.cache import Cache
from xTool.cache.constants import CacheBackendType, CacheInstanceType
from xTool.crypto.unique import SequenceManager, uniqid


def test_uniqid():
    actual = uniqid()
    # print(actual) # f5cf1a03a7ff368f9179419c344cfcd4
    assert len(actual) == 32


class TestSequenceManager:

    def test_generate(self):
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
        manager = SequenceManager(cache)
        assert manager.generate() == 1
        assert manager.generate() == 2
        assert manager.generate() == 3
        assert manager.generate() == 4

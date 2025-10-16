import fakeredis
import pytest

from xTool.cache import Cache
from xTool.cache.constants import CacheBackendType, CacheInstanceType


@pytest.fixture
def cache():
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
    return cache

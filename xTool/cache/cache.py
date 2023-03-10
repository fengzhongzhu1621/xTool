# -*- coding: utf-8 -*-
import logging
import sys

from .constants import CacheBackendType, CacheInstanceType
from .storage.memory import InstanceCache
from .storage.redis import BaseRedisCache, RedisCache, SentinelRedisCache

logger = logging.getLogger("cache")


class Cache:
    CacheTypes = {
        CacheInstanceType.RedisCache: RedisCache,
        CacheInstanceType.SentinelRedisCache: SentinelRedisCache,
        CacheInstanceType.InstanceCache: InstanceCache,
    }

    def __new__(
        cls,
        backend: CacheBackendType = CacheBackendType.CELERY,
        cache_instance_type: CacheInstanceType = CacheInstanceType.RedisCache,
        **kwargs
    ):
        try:
            # 根据类型动态创建不同的类实例
            redis_cache: BaseRedisCache = cls.CacheTypes[cache_instance_type]
            return redis_cache.instance(backend, **kwargs)
        except Exception as exc_info:
            logger.exception(
                "fail to use %s [%s] %s", backend, " ".join(sys.argv), exc_info
            )
            raise

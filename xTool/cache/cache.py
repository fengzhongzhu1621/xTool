# -*- coding: utf-8 -*-
import logging
import sys

from .constants import CacheInstanceType
from .storage.memory import InstanceCache
from .storage.redis import RedisCache, SentinelRedisCache

logger = logging.getLogger("cache")


class Cache:
    CacheTypes = {
        CacheInstanceType.RedisCache: RedisCache,
        CacheInstanceType.SentinelRedisCache: SentinelRedisCache,
        CacheInstanceType.InstanceCache: InstanceCache,
    }

    def __new__(cls, backend, cache_instance_type: CacheInstanceType, **kwargs):
        try:
            # 根据类型动态创建不同的类实例
            type_ = cls.CacheTypes[cache_instance_type]
            return type_.instance(backend, **kwargs)
        except Exception:
            logger.exception("fail to use %s [%s]", backend, " ".join(sys.argv))
            raise

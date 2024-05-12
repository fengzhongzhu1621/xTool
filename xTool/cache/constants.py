from enum import Enum

TASK_STORAGE_QUEUE = "task_storage"
TASK_DELAY_QUEUE = "task_delay_queue"


class CacheBackendType(Enum):
    CELERY = "celery"
    SERVICE = "service"
    QUEUE = "queue"
    CACHE = "cache"
    LOG = "log"


class CacheInstanceType(Enum):
    RedisCache = "RedisCache"
    SentinelRedisCache = "SentinelRedisCache"
    InstanceCache = "InstanceCache"

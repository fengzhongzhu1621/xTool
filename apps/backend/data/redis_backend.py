from django.conf import settings

from apps.backend.data.base_backend import BaseDataBackend


class RedisDataBackend(BaseDataBackend):
    def exists(self, key: str) -> bool:
        """判断 key 是否存在 ."""
        key = f"{settings.REDIS_KEY_PREFIX}:{key}"
        return settings.REDIS_INST.exists(key)

    def incr_expireat(self, key: str, amount: int, when=None) -> int:
        key = f"{settings.REDIS_KEY_PREFIX}:{key}"
        value = settings.REDIS_INST.incrby(key, amount)
        if when:
            settings.REDIS_INST.expireat(key, when)
        return value

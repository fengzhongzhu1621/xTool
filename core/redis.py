from django.core.cache import cache as redis_cache
from django_redis.pool import ConnectionFactory as Factory


def get_redis_client():
    redis_client = redis_cache.client.get_client()
    return redis_client


class ConnectionFactory(Factory):
    """
    自定义ConnectionFactory以注入decode_responses参数
    """

    def make_connection_params(self, url):
        kwargs = super().make_connection_params(url)
        kwargs["decode_responses"] = True
        return kwargs

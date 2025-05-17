from django.core.cache import cache as redis_cache


def get_redis_client():
    redis_client = redis_cache.client.get_client()
    return redis_client

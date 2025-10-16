import os
import traceback

import redis
from django.apps import AppConfig
from django.conf import settings
from redis.sentinel import Sentinel

from apps.logger import logger


def get_client_through_sentinel():
    kwargs = {"password": settings.REDIS_PASSWORD}
    host = settings.REDIS_HOST
    port = settings.REDIS_PORT
    sentinels = list(zip([h.strip() for h in host.split(",")], [p.strip() for p in str(port).split(",")]))
    rs = Sentinel(sentinels, **kwargs)
    # avoid None value in settings.REDIS
    r = rs.master_for(os.getenv("BKAPP_REDIS_SERVICE_NAME", "mymaster"))
    # try to connect master
    r.echo("Hello Redis")
    return r


def get_cluster_client():
    from rediscluster import RedisCluster

    kwargs = {
        "startup_nodes": [{"host": settings.REDIS_HOST, "port": settings.REDIS_PORT}],
        "password": settings.REDIS_PASSWORD,
    }
    r = RedisCluster(**kwargs)
    r.echo("Hello Redis")
    return r


def get_single_client():
    kwargs = {
        "host": settings.REDIS_HOST,
        "port": settings.REDIS_PORT,
        "password": settings.REDIS_PASSWORD,
        "db": settings.REDIS_DB,
    }

    pool = redis.ConnectionPool(**kwargs)
    return redis.StrictRedis(connection_pool=pool)


CLIENT_GETTER = {
    "replication": get_client_through_sentinel,
    "cluster": get_cluster_client,
    "single": get_single_client,
}


class BackendAppConfig(AppConfig):
    name = "apps.backend"

    def ready(self):
        # init redis pool
        mode = settings.DATA_BACKEND_REDIS_MODE
        try:
            settings.REDIS_INST = CLIENT_GETTER[mode]()
        except Exception:  # pylint: disable=broad-except
            # fall back to single node mode
            logger.error("redis client init error: %s" % traceback.format_exc())

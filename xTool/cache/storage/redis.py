# -*- coding: utf-8 -*-
import abc
import copy
import logging
import time
import uuid
from copy import deepcopy
from typing import Dict

import ujson as json
from redis.exceptions import ConnectionError
from redis.sentinel import Sentinel
from xTool.cache.constants import TASK_DELAY_QUEUE, TASK_STORAGE_QUEUE, CacheBackendType

import redis

logger = logging.getLogger("cache")

__all__ = ["BaseRedisCache", "RedisCache", "SentinelRedisCache"]


class BaseRedisCache(abc.ABC):
    def __init__(
        self, connection_conf: Dict, redis_class=None, refresh_connect_max: int = 3
    ) -> None:
        self.connection_conf = connection_conf
        self.redis_class = redis_class if redis_class else redis.Redis
        self._instance = None
        # 记录刷新时间
        self.refresh_time = 0
        # 最大刷新次数
        self.refresh_connect_max = refresh_connect_max
        # 创建redis连接
        self.refresh_instance()

    @classmethod
    def instance(cls, backend: CacheBackendType, connection_conf: Dict, **kwargs):
        """获得redis客户端实例 ."""
        cls_instance = "_%s_instance" % backend.value
        if not hasattr(cls, cls_instance):
            # 使用自定义配置创建redis连接
            ins = cls(connection_conf, **kwargs)
            setattr(cls, cls_instance, ins)
            return ins
        return getattr(cls, cls_instance)

    @abc.abstractmethod
    def create_instance(self):
        """创建连接 ."""
        raise NotImplementedError()

    @abc.abstractmethod
    def close_instance(self, instance=None):
        """关闭连接 ."""
        raise NotImplementedError()

    def refresh_instance(self):
        """重连redis ."""
        # redis重连
        if self._instance is not None:
            self.close_instance(self._instance)

        # 失败重试
        exception = None
        for _ in range(self.refresh_connect_max):
            try:
                self._instance = self.create_instance()
                # 记录重连时间
                self.refresh_time = time.time()
                break
            except Exception as exc_info:  # noqa
                exception = exc_info
                logger.exception(exc_info)
        if exception:
            raise exception

    def __getattr__(self, name):
        command = getattr(self._instance, name)

        def handle(*args, **kwargs):
            exception = None
            for _ in range(self.refresh_connect_max):
                try:
                    return command(*args, **kwargs)
                except ConnectionError as exc_info:  # noqa
                    exception = exc_info
                    self.refresh_instance()
                except Exception as exc_info:  # noqa
                    raise exc_info
            if exception:
                raise exception

        return handle

    def delay(self, cmd: str, queue: str, prefix: str = None, *values, **kwargs):
        """延时推入队列 ."""
        # 任务的得分
        delay = kwargs.get("delay", 0)
        if delay < 0:
            delay = 0
        score = time.time() + delay
        # 生成任务ID
        task_id = kwargs.get("task_id", str(uuid.uuid4()))
        # 构造任务的信息
        message = json.dumps([task_id, cmd, queue, values, score])
        # 将任务ID的详情存放到哈希表中
        self.hset(f"{prefix}{TASK_STORAGE_QUEUE}", task_id, message)
        # 将任务ID记录到有序集合，分数为入队时间戳
        self.zadd(f"{prefix}{TASK_DELAY_QUEUE}", task_id, score)


class RedisCache(BaseRedisCache):
    """ """

    def __init__(
        self,
        connection_conf,
        redis_class=None,
        refresh_connect_max: int = 3,
        decode_responses=True,
        encoding="utf-8",
    ):
        if decode_responses:
            # 插入默认参数
            new_connection_conf = deepcopy(connection_conf)
            new_connection_conf.update({"decode_responses": True, "encoding": encoding})
        else:
            new_connection_conf = connection_conf
        super().__init__(
            new_connection_conf,
            redis_class=redis_class,
            refresh_connect_max=refresh_connect_max,
        )

    def create_instance(self):
        return self.redis_class(**self.connection_conf)

    def close_instance(self, instance=None):
        if instance:
            instance.connection_pool.disconnect()


class SentinelRedisCache(BaseRedisCache):
    def __init__(
        self,
        connection_conf,
        redis_class=None,
        refresh_connect_max=None,
        decode_responses=True,
        socket_timeout: int = 60,
        master_name="mymaster",
        sentinel_password="",
        redis_password="",
        encoding="utf-8",
    ):
        new_connection_conf = copy.deepcopy(connection_conf)
        self.sentinel_host = new_connection_conf.pop("host")
        self.sentinel_port = new_connection_conf.pop("port")
        self.socket_timeout = int(
            new_connection_conf.pop("socket_timeout", socket_timeout)
        )
        self.master_name = new_connection_conf.pop("master_name", master_name)
        self.cache_mode = new_connection_conf.pop("cache_mode", "master")
        self.sentinel_password = (
            new_connection_conf.pop("sentinel_password", "") or sentinel_password
        )
        self.redis_password = (
            new_connection_conf.pop("redis_password", "") or redis_password
        )
        # 插入默认参数
        if decode_responses:
            new_connection_conf.update({"decode_responses": True, "encoding": encoding})
        super().__init__(
            new_connection_conf,
            redis_class=redis_class,
            refresh_connect_max=refresh_connect_max,
        )

    def create_instance(self):
        sentinel_kwargs = {
            "socket_connect_timeout": self.socket_timeout,
        }
        if self.sentinel_password:
            sentinel_kwargs["password"] = self.sentinel_password
        # 连接哨兵服务器
        redis_sentinel = Sentinel(
            [
                (
                    self.sentinel_host,
                    self.sentinel_port,
                )
            ],
            sentinel_kwargs=sentinel_kwargs,
        )

        redis_instance_config = self.connection_conf
        redis_instance_config["password"] = self.redis_password

        # 获得主服务器
        instance = redis_sentinel.master_for(
            self.master_name, redis_class=self.redis_class, **redis_instance_config
        )
        # 关闭与其它哨兵的连接
        list(map(self.close_instance, redis_sentinel.sentinels))

        return instance

    def close_instance(self, instance=None):
        if instance:
            instance.connection_pool.disconnect()

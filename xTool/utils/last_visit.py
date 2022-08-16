# -*- coding: utf-8 -*-

from typing import List
import time

import arrow
from django.utils import timezone


def activate(redis_client, key: str, field: str, value: str) -> None:
    """加入到最近访问记录 ."""
    field = str(field).strip()
    if not field:
        return
    # 获得最近的使用时间
    score = int(time.time())
    # 加入到有序集合，用于根据时间段获取field列表
    redis_client.zadd(f"{key}:time", score, field)
    value = value.strip() if value else ""
    if value:
        # 存储value值
        redis_client.hset(key, field, value)


def deactivate(redis_client, key: str, field: str) -> int:
    """从最近访问记录中移除field ."""
    field = str(field).strip()
    if not field:
        return
    # 移除field
    return redis_client.zrem(f"{key}:time", field)


def get_value(redis_client, key: str, field: str) -> str:
    """获得field的值 ."""
    return redis_client.hget(key, field)


def get_all_fields(redis_client, key: str) -> List:
    """从最近的访问记录中获取所有的field和分数 ."""
    return [
        item
        for item in redis_client.zrange(f"{key}:time", 0, -1, withscores=True)
        if item[0]
    ]


def get_all_fields_with_current_timezone(
    redis_client, key: str, datetime_format: str = "YYYY-MM-DD HH:mm:ss"
) -> List:
    """从最近的访问记录中获取所有的field和分数 ."""
    data = get_all_fields(redis_client, key)
    result = [
        (
            item[0],
            arrow.get(item[1])
            .to(timezone.get_current_timezone().zone)
            .format(datetime_format),
        )
        for item in data
    ]
    return result


def get_activate_fields(redis_client, key: str, expired_time: int) -> List:
    """逆序获得最近指定时间段的记录 ."""
    # 获得时间范围
    # ------------------------------------------> 时间
    #   |                     |
    # min_score              max_score
    max_score = int(time.time())
    min_score = max_score - expired_time
    return redis_client.zrevrangebyscore(f"{key}:time", max_score, min_score)

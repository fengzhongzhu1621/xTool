# -*- coding: utf-8 -*-

from datetime import datetime

from django.utils import timezone
from django.utils.dateparse import parse_datetime


def localtime(value):
    """转换为本地时间 ."""
    if timezone.is_aware(value):
        # 如果value包含时区，则转换为settings.TIME_ZONE
        return timezone.localtime(value)
    # 如果value不包含时区，则添加当前时区
    return timezone.make_aware(value)


def strftime_localtime(value, datetime_format="%Y-%m-%d %H:%M:%S%z"):
    """将当前时区转换为字符串格式 ."""
    return localtime(value).strftime(datetime_format)


def from_iso_format(start_time: str) -> datetime:
    """将iso8601格式的字符串转换为当前时区的时间对象（无时区） ."""
    start_time_obj = parse_datetime(start_time)
    # 获得当前时区
    current_timezone = timezone.get_current_timezone()
    # 转换为当前时区的时间
    start_at_current_timezone = start_time_obj.astimezone(current_timezone)
    # 去掉时区
    start_at_current_timezone_naive = timezone.make_naive(start_at_current_timezone)
    return start_at_current_timezone_naive

# -*- coding: utf-8 -*-

from django.utils import timezone


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

from datetime import datetime

import arrow
from dateutil.tz import tzutc
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.settings import api_settings


def humanize_datetime(value: datetime, datetime_format="YYYY-MM-DD HH:mm:ss") -> str:
    """将datetime对象转换为本地时区的字符串格式 ."""
    if not value:
        return ""
    deadline_time = arrow.get(value).to(settings.TIME_ZONE).format(datetime_format)

    return deadline_time


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


def format_date_string(date_string: str, output_format: str = api_settings.DATETIME_FORMAT):
    """将时间字符串格式化为指定的日期格式 ."""
    try:
        date = arrow.get(date_string)
        if isinstance(date.tzinfo, tzutc):
            date = date.replace(tzinfo=timezone.get_default_timezone())
        else:
            date = date.astimezone(timezone.get_default_timezone())
        return date.strftime(output_format)
    except Exception:  # pylint: disable=broad-except
        return date_string


def strftime_local(aware_time, fmt="%Y-%m-%d %H:%M:%S"):
    """
    格式化aware_time为本地时间

    :param {datetime} aware_time 时间字段
    :param {string} fmt 时间format格式
    :return 格式化时间字符串
    """
    if not aware_time:
        # 当时间字段允许为NULL时，直接返回None
        return None
    if timezone.is_aware(aware_time):
        # translate to time in local timezone
        aware_time = timezone.localtime(aware_time)
    return aware_time.strftime(fmt)


def from_iso_format(start_time: str) -> datetime:
    """将iso8601格式的字符串转换为当前时区的时间对象 ."""
    start_time_obj = parse_datetime(start_time)
    # 转换为当前时区的时间
    current_timezone = timezone.get_current_timezone()
    start_at_current_timezone = start_time_obj.astimezone(current_timezone)
    start_at_current_timezone_naive = timezone.make_naive(start_at_current_timezone)
    return start_at_current_timezone_naive

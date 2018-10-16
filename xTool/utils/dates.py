# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from xTool.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # for doctest
import six

from croniter import croniter


cron_presets = {
    '@hourly': '0 * * * *',
    '@daily': '0 0 * * *',
    '@weekly': '0 0 * * 0',
    '@monthly': '0 0 1 * *',
    '@yearly': '0 0 1 1 *',
}


def date_range(
        start_date,
        end_date=None,
        num=None,
        delta=None):
    """
    Get a set of dates as a list based on a start, end and delta, delta
    can be something that can be added to ``datetime.datetime``
    or a cron expression as a ``str``

    :param start_date: anchor date to start the series from
    :type start_date: datetime.datetime
    :param end_date: right boundary for the date range
    :type end_date: datetime.datetime
    :param num: alternatively to end_date, you can specify the number of
        number of entries you want in the range. This number can be negative,
        output will always be sorted regardless
    :type num: int

    >>> date_range(datetime(2016, 1, 1), datetime(2016, 1, 3), delta=timedelta(1))
    [datetime.datetime(2016, 1, 1, 0, 0), datetime.datetime(2016, 1, 2, 0, 0), datetime.datetime(2016, 1, 3, 0, 0)]
    >>> date_range(datetime(2016, 1, 1), datetime(2016, 1, 3), delta='0 0 * * *')
    [datetime.datetime(2016, 1, 1, 0, 0), datetime.datetime(2016, 1, 2, 0, 0), datetime.datetime(2016, 1, 3, 0, 0)]
    >>> date_range(datetime(2016, 1, 1), datetime(2016, 3, 3), delta="0 0 0 * *")
    [datetime.datetime(2016, 1, 1, 0, 0), datetime.datetime(2016, 2, 1, 0, 0), datetime.datetime(2016, 3, 1, 0, 0)]
    """
    if not delta:
        return []
    if end_date and start_date > end_date:
        raise Exception("Wait. start_date needs to be before end_date")
    if end_date and num:
        raise Exception("Wait. Either specify end_date OR num")
    # 结束时间默认为当前UTC时间
    if not end_date and not num:
        end_date = timezone.system_now()

    delta_iscron = False
    tz = start_date.tzinfo
    if isinstance(delta, six.string_types):
        delta_iscron = True
        # 去掉开始时间的时区
        if tz is not None:
            start_date = timezone.make_naive(start_date, tz)
        cron = croniter(delta, start_date)
    elif isinstance(delta, timedelta):
        delta = abs(delta)

    l = []
    if end_date:
        while start_date <= end_date:
            if timezone.is_naive(start_date):
                l.append(timezone.make_aware(start_date, tz))
            else:
                l.append(start_date)

            if delta_iscron:
                start_date = cron.get_next(datetime)
            else:
                start_date += delta
    else:
        for _ in range(abs(num)):
            if timezone.is_naive(start_date):
                # 如果开始时间不存在时区信息，加上指定的时区信息
                # 如果没有指定时区信息，默认系统时区
                l.append(timezone.make_aware(start_date, tz))
            else:
                l.append(start_date)

            if delta_iscron:
                if num > 0:
                    start_date = cron.get_next(datetime)
                else:
                    start_date = cron.get_prev(datetime)
            else:
                if num > 0:
                    start_date += delta
                else:
                    start_date -= delta
    return sorted(l)


def round_time(dt, delta, start_date=timezone.make_aware(datetime.min)):
    """日期四舍五入，范围[start_date, start_date + delta]
    Returns the datetime of the form start_date + i * delta
    which is closest to dt for any non-negative integer i.

    Note that delta may be a datetime.timedelta or a dateutil.relativedelta

    datetime.min 按天四舍五入
    relativedelta(months=1) 按月四舍五入

    >>> round_time(datetime(2015, 1, 1, 6), timedelta(days=1))
    datetime.datetime(2015, 1, 1, 0, 0)
    >>> round_time(datetime(2015, 1, 2), relativedelta(months=1))
    datetime.datetime(2015, 1, 1, 0, 0)

    >>> round_time(datetime(2015, 9, 16, 0, 0), timedelta(1), datetime(2015, 9, 14, 0, 0))
    datetime.datetime(2015, 9, 16, 0, 0)
    >>> round_time(datetime(2015, 9, 15, 0, 0), timedelta(1), datetime(2015, 9, 14, 0, 0))
    datetime.datetime(2015, 9, 15, 0, 0)
    >>> round_time(datetime(2015, 9, 14, 0, 0), timedelta(1), datetime(2015, 9, 14, 0, 0))
    datetime.datetime(2015, 9, 14, 0, 0)
    >>> round_time(datetime(2015, 9, 13, 0, 0), timedelta(1), datetime(2015, 9, 14, 0, 0))
    datetime.datetime(2015, 9, 14, 0, 0)
    """
    if isinstance(delta, six.string_types):
        # 获得上一个周期的时间
        # It's cron based, so it's easy
        tz = start_date.tzinfo
        if tz is not None:
            start_date = timezone.make_naive(start_date, tz)
        cron = croniter(delta, start_date)
        prev = cron.get_prev(datetime)
        if prev == start_date:
            return timezone.make_aware(start_date, tz)
        else:
            return timezone.make_aware(prev, tz)

    # Ignore the microseconds of dt
    dt -= timedelta(microseconds=dt.microsecond)

    # We are looking for a datetime in the form start_date + i * delta
    # which is as close as possible to dt. Since delta could be a relative
    # delta we don't know its exact length in seconds so we cannot rely on
    # division to find i. Instead we employ a binary search algorithm, first
    # finding an upper and lower limit and then disecting the interval until
    # we have found the closest match.

    # We first search an upper limit for i for which start_date + upper * delta
    # exceeds dt.
    upper = 1
    while start_date + upper*delta < dt:
        # To speed up finding an upper limit we grow this exponentially by a
        # factor of 2
        upper *= 2

    # Since upper is the first value for which start_date + upper * delta
    # exceeds dt, upper // 2 is below dt and therefore forms a lower limited
    # for the i we are looking for
    lower = upper // 2

    # We now continue to intersect the interval between
    # start_date + lower * delta and start_date + upper * delta
    # until we find the closest value
    while True:
        # Invariant: start + lower * delta < dt <= start + upper * delta
        # If start_date + (lower + 1)*delta exceeds dt, then either lower or
        # lower+1 has to be the solution we are searching for
        if start_date + (lower + 1)*delta >= dt:
            # Check if start_date + (lower + 1)*delta or
            # start_date + lower*delta is closer to dt and return the solution
            if (
                    (start_date + (lower + 1) * delta) - dt <=
                    dt - (start_date + lower * delta)):
                return start_date + (lower + 1)*delta
            else:
                return start_date + lower * delta

        # We intersect the interval and either replace the lower or upper
        # limit with the candidate
        candidate = lower + (upper - lower) // 2
        if start_date + candidate*delta >= dt:
            upper = candidate
        else:
            lower = candidate

    # in the special case when start_date > dt the search for upper will
    # immediately stop for upper == 1 which results in lower = upper // 2 = 0
    # and this function returns start_date.


def infer_time_unit(time_seconds_arr):
    """时间的表示方式
    Determine the most appropriate time unit for an array of time durations
    specified in seconds.

    e.g. 5400 seconds => 'minutes', 36000 seconds => 'hours'
    """
    # 默认时间的单位是小时
    if len(time_seconds_arr) == 0:
        return 'hours'
    max_time_seconds = max(time_seconds_arr)
    # 如果小于2分钟，则用秒表示
    if max_time_seconds <= 60*2:
        return 'seconds'
    # 如果小于2小时，用分钟表示
    elif max_time_seconds <= 60*60*2:
        return 'minutes'
    # 如果小于2天，用小时表示
    elif max_time_seconds <= 24*60*60*2:
        return 'hours'
    # 否则用天表示
    else:
        return 'days'


def scale_time_units(time_seconds_arr, unit):
    """将时间转换为指定的单位表示
    Convert an array of time durations in seconds to the specified time unit.
    """
    if unit == 'minutes':
        return list(map(lambda x: x*1.0/60, time_seconds_arr))
    elif unit == 'hours':
        return list(map(lambda x: x*1.0/(60*60), time_seconds_arr))
    elif unit == 'days':
        return list(map(lambda x: x*1.0/(24*60*60), time_seconds_arr))
    return time_seconds_arr


def days_ago(n, hour=0, minute=0, second=0, microsecond=0):
    """
    Get a datetime object representing `n` days ago. By default the time is
    set to midnight.
    """
    today = timezone.utcnow().replace(
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond)
    return today - timedelta(days=n)


def parse_execution_date(execution_date_str):
    """
    Parse execution date string to datetime object.
    """
    return timezone.parse(execution_date_str)


def rfc3339_datetime_re( anchor=True ):
    """
    Returns a regular expression for syntactic validation of ISO date-times, RFC-3339 date-times
    to be precise.


    >>> bool( rfc3339_datetime_re().match('2013-11-06T15:56:39Z') )
    True

    >>> bool( rfc3339_datetime_re().match('2013-11-06T15:56:39.123Z') )
    True

    >>> bool( rfc3339_datetime_re().match('2013-11-06T15:56:39-08:00') )
    True

    >>> bool( rfc3339_datetime_re().match('2013-11-06T15:56:39.123+11:00') )
    True

    It anchors the matching to the beginning and end of a string by default ...

    >>> bool( rfc3339_datetime_re().search('bla 2013-11-06T15:56:39Z bla') )
    False

    ... but that can be changed:

    >>> bool( rfc3339_datetime_re( anchor=False ).search('bla 2013-11-06T15:56:39Z bla') )
    True

    >>> bool( rfc3339_datetime_re( anchor=False ).match('2013-11-06T15:56:39Z bla') )
    True

    Keep in mind that re.match() always anchors at the beginning:

    >>> bool( rfc3339_datetime_re( anchor=False ).match('bla 2013-11-06T15:56:39Z') )
    False

    It does not check whether the actual value is a semantically valid datetime:

    >>> bool( rfc3339_datetime_re().match('9999-99-99T99:99:99.9-99:99') )
    True

    If the regular expression matches, each component of the matching value will be exposed as a
    captured group in the match object.

    >>> rfc3339_datetime_re().match('2013-11-06T15:56:39Z').groups()
    ('2013', '11', '06', '15', '56', '39', None, 'Z')
    >>> rfc3339_datetime_re().match('2013-11-06T15:56:39.123Z').groups()
    ('2013', '11', '06', '15', '56', '39', '123', 'Z')
    >>> rfc3339_datetime_re().match('2013-11-06T15:56:39.123-08:30').groups()
    ('2013', '11', '06', '15', '56', '39', '123', '-08:30')
    """
    return re.compile(
        ('^' if anchor else '') +
        '(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})' +
        ('$' if anchor else '') )


_rfc3339_datetime_re = rfc3339_datetime_re( )


def parse_iso_utc( s ):
    """
    Parses an ISO time with a hard-coded Z for zulu-time (UTC) at the end. Other timezones are
    not supported.

    :param str s: the ISO-formatted time

    :rtype: datetime.datetime

    :return: an timezone-naive datetime object

    >>> parse_iso_utc('2016-04-27T00:28:04.000Z')
    datetime(2016, 4, 27, 0, 28, 4)
    >>> parse_iso_utc('2016-04-27T00:28:04Z')
    datetime(2016, 4, 27, 0, 28, 4)
    >>> parse_iso_utc('2016-04-27T00:28:04X')
    Traceback (most recent call last):
    ...
    ValueError: Not a valid ISO datetime in UTC: 2016-04-27T00:28:04X
    """
    m = _rfc3339_datetime_re.match( s )
    if not m:
        raise ValueError( 'Not a valid ISO datetime in UTC: ' + s )
    else:
        fmt = '%Y-%m-%dT%H:%M:%S' + ('.%f' if m.group( 7 ) else '') + 'Z'
        return datetime.strptime( s, fmt )

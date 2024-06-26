from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime as dt
from datetime import datetime, timedelta
from timeit import default_timer

import arrow
import six
from croniter import croniter

from xTool.utils import timezone

# Use timer that's not susceptible to time of day adjustments.
try:
    # perf_counter is only present on Py3.3+
    from time import perf_counter as time_now
except ImportError:
    # fall back to using time
    from time import time as time_now

# 调度缩写
cron_presets = {
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
}


def date_range(start_date, end_date=None, num=None, delta=None):
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
    if not end_date and not num:
        end_date = datetime.now()

    delta_iscron = False
    if isinstance(delta, six.string_types):
        delta_iscron = True
        cron = croniter(delta, start_date)
    elif isinstance(delta, timedelta):
        delta = abs(delta)

    dates = []
    if end_date:
        while start_date <= end_date:
            dates.append(start_date)
            if delta_iscron:
                start_date = cron.get_next(datetime)
            else:
                start_date += delta
    else:
        for _ in range(abs(num)):
            dates.append(start_date)
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
    return sorted(dates)


def round_time(dt, delta, start_date=datetime.min):
    """日期四舍五入，范围[start_date, start_date + delta]
    Returns the datetime of the form start_date + i * delta
    which is closest to dt for any non-negative integer i.
    Note that delta may be a datetime.timedelta or a dateutil.relativedelta
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
        # It's cron based, so it's easy
        cron = croniter(delta, start_date)
        prev = cron.get_prev(datetime)
        if prev == start_date:
            return start_date
        else:
            return prev

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
    while start_date + upper * delta < dt:
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
        if start_date + (lower + 1) * delta >= dt:
            # Check if start_date + (lower + 1)*delta or
            # start_date + lower*delta is closer to dt and return the solution
            if (start_date + (lower + 1) * delta) - dt <= dt - (start_date + lower * delta):
                return start_date + (lower + 1) * delta
            else:
                return start_date + lower * delta

        # We intersect the interval and either replace the lower or upper
        # limit with the candidate
        candidate = lower + (upper - lower) // 2
        if start_date + candidate * delta >= dt:
            upper = candidate
        else:
            lower = candidate

    # in the special case when start_date > dt the search for upper will
    # immediately stop for upper == 1 which results in lower = upper // 2 = 0
    # and this function returns start_date.


def infer_time_unit(time_seconds_arr):
    """
    Determine the most appropriate time unit for an array of time durations
    specified in seconds.
    e.g. 5400 seconds => 'minutes', 36000 seconds => 'hours'
    """
    if len(time_seconds_arr) == 0:
        return "hours"
    max_time_seconds = max(time_seconds_arr)
    if max_time_seconds <= 60 * 2:
        return "seconds"
    elif max_time_seconds <= 60 * 60 * 2:
        return "minutes"
    elif max_time_seconds <= 24 * 60 * 60 * 2:
        return "hours"
    else:
        return "days"


def scale_time_units(time_seconds_arr, unit):
    """
    Convert an array of time durations in seconds to the specified time unit.
    """
    if unit == "minutes":
        return list(map(lambda x: x * 1.0 / 60, time_seconds_arr))
    elif unit == "hours":
        return list(map(lambda x: x * 1.0 / (60 * 60), time_seconds_arr))
    elif unit == "days":
        return list(map(lambda x: x * 1.0 / (24 * 60 * 60), time_seconds_arr))
    return time_seconds_arr


def days_ago(n, hour=0, minute=0, second=0, microsecond=0):
    """
    Get a datetime object representing `n` days ago. By default the time is
    set to midnight.
    """
    today = datetime.today().replace(hour=hour, minute=minute, second=second, microsecond=microsecond)
    return today - timedelta(days=n)


def parse_execution_date(execution_date_str):
    """
    Parse execution date string to datetime object.
    """
    o = timezone.parse(execution_date_str)
    # 去掉时区信息
    # cross library compatibility
    naive = dt.datetime(o.year, o.month, o.day, o.hour, o.minute, o.second, o.microsecond)
    return naive


def ds_add(ds, days):
    """
    Add or subtract days from a YYYY-MM-DD

    :param ds: anchor date in ``YYYY-MM-DD`` format to add to
    :type ds: str
    :param days: number of days to add to the ds, you can use negative values
    :type days: int

    >>> ds_add('2015-01-01', 5)
    '2015-01-06'
    >>> ds_add('2015-01-06', -5)
    '2015-01-01'
    """

    ds = datetime.strptime(ds, "%Y-%m-%d")
    if days:
        ds = ds + timedelta(days)
    return ds.isoformat()[:10]


def ds_format(ds, input_format, output_format):
    """
    Takes an input string and outputs another string
    as specified in the output format

    :param ds: input string which contains a date
    :type ds: str
    :param input_format: input string format. E.g. %Y-%m-%d
    :type input_format: str
    :param output_format: output string format  E.g. %Y-%m-%d
    :type output_format: str

    >>> ds_format('2015-01-01', "%Y-%m-%d", "%m-%d-%y")
    '01-01-15'
    >>> ds_format('1/5/2015', "%m/%d/%Y",  "%Y-%m-%d")
    '2015-01-05'
    """
    return datetime.strptime(ds, input_format).strftime(output_format)


def now() -> arrow.Arrow:
    return arrow.now()


def date_to_string(_data):
    """
    传入一个标准日期，返回其字符串形式
    :param {datetime} _data: 日期
    :return: 日期字符串
    """
    return _data.strftime("%Y-%m-%d")


def Time():
    """Returns some representation of the current time.

    This wrapper is meant to take advantage of a higher time
    resolution when available. Thus, its return value should be
    treated as an opaque object. It can be compared to the current
    time with TimeSince().
    """
    return default_timer()


def TimeSince(t):
    """Compares a value returned by Time() to the current time.

    Returns:
      the time since t, in fractional seconds.
    """
    return default_timer() - t


def PowersOf(logbase, count, lower=0, include_zero=True):
    """Returns a list of count powers of logbase (from logbase**lower)."""
    if not include_zero:
        return [logbase**i for i in range(lower, count + lower)]
    else:
        return [0] + [logbase**i for i in range(lower, count + lower)]

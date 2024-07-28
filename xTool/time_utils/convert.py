from datetime import datetime


def date_to_string(_data):
    """
    传入一个标准日期，返回其字符串形式
    :param {datetime} _data: 日期
    :return: 日期字符串
    """
    return _data.strftime("%Y-%m-%d")


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

#coding: utf-8

from datetime import datetime
from datetime import timedelta

from xTool.utils.dates import *
from xTool.utils.timezone import *


def test_date_range():
    actual = date_range(datetime(2016, 1, 1), datetime(2016, 1, 3), delta=timedelta(1))
    expected = [system_datetime(2016, 1, 1, 0, 0),
                system_datetime(2016, 1, 2, 0, 0),
                system_datetime(2016, 1, 3, 0, 0)]
    assert expected == actual

    actual = date_range(datetime(2016, 1, 1), datetime(2016, 1, 3), delta=timedelta(2))
    expected = [system_datetime(2016, 1, 1, 0, 0),
                system_datetime(2016, 1, 3, 0, 0)]
    assert expected == actual

    actual = date_range(datetime(2016, 1, 1), datetime(2016, 1, 3), delta=timedelta(3))
    expected = [system_datetime(2016, 1, 1, 0, 0)]
    assert expected == actual

    actual = date_range(datetime(2016, 1, 1),
                        datetime(2016, 1, 3),
                        delta='0 0 * * *')
    expected = [system_datetime(2016, 1, 1, 0, 0),
                system_datetime(2016, 1, 2, 0, 0),
                system_datetime(2016, 1, 3, 0, 0)]
    assert expected == actual

    actual = date_range(datetime(2016, 1, 1), datetime(2016, 3, 3), delta="0 0 0 * *")
    expected = [system_datetime(2016, 1, 1, 0, 0),
                system_datetime(2016, 2, 1, 0, 0),
                system_datetime(2016, 3, 1, 0, 0)]
    assert expected == actual


def test_round_time():
    actual = round_time(system_datetime(2015, 1, 1, 6), timedelta(days=1))
    expected = system_datetime(2015, 1, 1, 0, 0)
    assert expected == actual

    actual = round_time(None, "0 0 0 * *", start_date=datetime(2015, 1, 1, 6))
    expected = system_datetime(2015, 1, 1, 0, 0)
    assert expected == actual

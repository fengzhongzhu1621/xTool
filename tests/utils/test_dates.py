# coding: utf-8

import datetime as dt
from datetime import timedelta

from xTool.utils.dates import *
from xTool.utils.timezone import *


def test_date_range():
    actual = date_range(dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 3), delta=timedelta(1))
    expected = [dt.datetime(2016, 1, 1, 0, 0),
                dt.datetime(2016, 1, 2, 0, 0),
                dt.datetime(2016, 1, 3, 0, 0)]
    assert expected == actual

    actual = date_range(dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 3), delta=timedelta(2))
    expected = [dt.datetime(2016, 1, 1, 0, 0),
                dt.datetime(2016, 1, 3, 0, 0)]
    assert expected == actual

    actual = date_range(dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 3), delta=timedelta(3))
    expected = [dt.datetime(2016, 1, 1, 0, 0)]
    assert expected == actual

    actual = date_range(dt.datetime(2016, 1, 1),
                        dt.datetime(2016, 1, 3),
                        delta='0 0 * * *')
    expected = [dt.datetime(2016, 1, 1, 0, 0),
                dt.datetime(2016, 1, 2, 0, 0),
                dt.datetime(2016, 1, 3, 0, 0)]
    assert expected == actual

    actual = date_range(dt.datetime(2016, 1, 1), dt.datetime(2016, 3, 3), delta="0 0 0 * *")
    expected = [dt.datetime(2016, 1, 1, 0, 0),
                dt.datetime(2016, 2, 1, 0, 0),
                dt.datetime(2016, 3, 1, 0, 0)]
    assert expected == actual


def test_round_time():
    actual = round_time(dt.datetime(2015, 1, 1, 6), timedelta(days=1))
    expected = dt.datetime(2015, 1, 1, 0, 0)
    assert expected == actual

    actual = round_time(None, "0 0 0 * *", start_date=dt.datetime(2015, 1, 1, 6))
    expected = dt.datetime(2015, 1, 1, 0, 0)
    assert expected == actual


def test_infer_time_unit():
    actual = infer_time_unit([])
    expected = 'hours'
    assert expected == actual

    actual = infer_time_unit([120])
    expected = 'seconds'
    assert expected == actual

    actual = infer_time_unit([60*60*2])
    expected = 'minutes'
    assert expected == actual

    actual = infer_time_unit([24*60*60*2])
    expected = 'hours'
    assert expected == actual

    actual = infer_time_unit([24*60*60*365])
    expected = 'days'
    assert expected == actual


def test_scale_time_units():
    unit = 'minutes'
    actual = scale_time_units([120, 123, 60*60*2], unit)
    expected = [2.0, 2.05, 120.0]
    assert expected == actual

    unit = 'hours'
    actual = scale_time_units([360, 60 * 60, 60*60*2], unit)
    expected = [0.1, 1.0, 2.0]
    assert expected == actual

    unit = 'days'
    actual = scale_time_units([60*60*24, 60*60*24*365], unit)
    expected = [1.0, 365.0]
    assert expected == actual


def test_parse_execution_date():
    actual_1 = parse_execution_date('2018-01-01')
    actual_2 = parse_execution_date('2018-01-01 00:00:00')
    actual_3 = parse_execution_date('2018-01-01T00:00:00')
    assert actual_1 == actual_2 == actual_3

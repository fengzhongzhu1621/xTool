import datetime as dt
from datetime import timedelta

from xTool.time_utils.range import date_range, round_time


def test_date_range():
    actual = date_range(dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 3), delta=timedelta(1))
    expected = [dt.datetime(2016, 1, 1, 0, 0), dt.datetime(2016, 1, 2, 0, 0), dt.datetime(2016, 1, 3, 0, 0)]
    assert expected == actual

    actual = date_range(dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 3), delta=timedelta(2))
    expected = [dt.datetime(2016, 1, 1, 0, 0), dt.datetime(2016, 1, 3, 0, 0)]
    assert expected == actual

    actual = date_range(dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 3), delta=timedelta(3))
    expected = [dt.datetime(2016, 1, 1, 0, 0)]
    assert expected == actual

    actual = date_range(dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 3), delta="0 0 * * *")
    expected = [dt.datetime(2016, 1, 1, 0, 0), dt.datetime(2016, 1, 2, 0, 0), dt.datetime(2016, 1, 3, 0, 0)]
    assert expected == actual

    actual = date_range(dt.datetime(2016, 1, 1), dt.datetime(2016, 3, 3), delta="0 0 1 * *")
    expected = [dt.datetime(2016, 1, 1, 0, 0), dt.datetime(2016, 2, 1, 0, 0), dt.datetime(2016, 3, 1, 0, 0)]
    assert expected == actual


def test_round_time():
    actual = round_time(dt.datetime(2015, 1, 1, 6), timedelta(days=1))
    expected = dt.datetime(2015, 1, 1, 0, 0)
    assert expected == actual

    actual = round_time(None, "0 0 1 * *", start_date=dt.datetime(2015, 1, 1, 6))
    expected = dt.datetime(2015, 1, 1, 0, 0)
    assert expected == actual

#coding: utf-8

import time
import sys
from datetime import datetime

import pytest
import pendulum

from xTool.utils.timezone import *


def test_get_default_timezone():
    timezone = get_default_timezone()
    assert timezone == TIMEZONE_SYSTEM
    assert timezone == pendulum.local_timezone()

    class Configration(object):
        def get_default_timezone(self):
            return 'UTC'
    conf = Configration()
    timezone = get_default_timezone(conf)
    assert timezone == TIMEZONE_UTC


def test_is_localized():
    now = utcnow()
    assert is_localized(now)


def test_utc_epoch():
    d = utc_epoch()
    assert d.year == 1970
    assert d.month == 1
    assert d.day == 1


def test_is_naive():
    now = datetime.now()
    assert is_naive(now)


def test_convert_to_utc():
    now = datetime.now()
    now_with_timezone = convert_to_utc(now)
    assert is_localized(now_with_timezone)
    now = utcnow()
    now_with_timezone = convert_to_utc(now)
    assert now == now_with_timezone
    d = datetime(1970, 1, 1)
    d1 = d.replace(tzinfo=TIMEZONE_SYSTEM)
    now_with_timezone = convert_to_utc(d1)
    assert d1.astimezone(TIMEZONE_UTC) == now_with_timezone
    now_with_timezone = convert_to_utc(d, timezone=TIMEZONE_SYSTEM)
    assert d1.astimezone(TIMEZONE_UTC) == now_with_timezone


def test_make_aware():
    d = datetime(1970, 1, 1)
    d1 = make_aware(d)
    assert d1.year == d.year
    assert is_localized(d1)
    with pytest.raises(ValueError):
        now = utcnow()
        d1 = make_aware(now)
    d2 = make_aware(d, TIMEZONE_UTC)
    assert d2.year == d.year
    assert is_localized(d2)
    assert d1 != d2


def test_make_naive():
    d = utc_epoch()
    d1 = make_naive(d)
    d2 = make_naive(d, TIMEZONE_SYSTEM)
    assert d1 == d2
    d3 = make_naive(d, TIMEZONE_UTC)
    assert d1 != d3
    d4 = datetime(1970, 1, 1)
    assert d4 == d3


def test_parse():
    d = datetime(1970, 1, 1)
    d1 = parse('1970-01-01 00:00:00')
    d2 = make_aware(d)
    assert d1 == d2
    d3 = parse('1970-01-01 00:00:00', TIMEZONE_UTC)
    d4 = utc_epoch()
    assert d3 == d4

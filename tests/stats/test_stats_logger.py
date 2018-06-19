#coding: utf-8

from datetime import datetime

from xTool.stats.stats_logger import DummyStatsLogger


class TestDummyStatsLogger:
    def test_classmethod(self):
        stat = None
        dt = datetime.now()
        assert DummyStatsLogger.incr(stat, count=1, rate=1) is None
        assert DummyStatsLogger.decr(stat, count=1, rate=1) is None
        assert DummyStatsLogger.gauge(stat, 1, rate=1, delta=False) is None
        assert DummyStatsLogger.timing(stat, dt) is None
